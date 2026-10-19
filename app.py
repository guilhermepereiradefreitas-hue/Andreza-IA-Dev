import os
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from database import get_db_connection
from google_sheets import GoogleSheetsUserService
from llm_service import gerar_resposta_llm
from rag_service import salvar_memoria_vetorial

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_super_segura")
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/charts', exist_ok=True)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

sheets_service = GoogleSheetsUserService()


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return User(id=user_data[0], username=user_data[1])
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data and bcrypt.check_password_hash(user_data[2], password):
            user = User(id=user_data[0], username=user_data[1])
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Conta criada com sucesso! Faça o login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("Erro ao registrar usuário (Nome já pode existir).", "danger")

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/google/auth")
@login_required
def google_auth():
    flow = sheets_service.criar_fluxo_autorizacao(url_for('google_callback', _external=True))
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['google_oauth_state'] = state
    return redirect(authorization_url)


@app.route("/google/callback")
@login_required
def google_callback():
    flow = sheets_service.criar_fluxo_autorizacao(url_for('google_callback', _external=True))
    flow.fetch_token(authorization_response=request.url)
    sheets_service.salvar_token_usuario(current_user.id, flow.credentials)
    flash("Conta Google conectada com sucesso!", "success")
    return redirect(url_for("index"))


@app.route("/api/google/status")
@login_required
def google_status():
    creds = sheets_service.obter_credenciais_usuario(current_user.id)
    return jsonify({"conectado": creds is not None})


@app.route("/")
@login_required
def index():
    hora = datetime.now().hour
    saudacao = "Bom dia" if 5 <= hora < 12 else ("Boa tarde" if 12 <= hora < 18 else "Boa noite")
    return render_template("index.html", saudacao=saudacao, username=current_user.username)


@app.route("/api/chats", methods=["GET"])
@login_required
def listar_chats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM chats WHERE user_id = %s ORDER BY created_at DESC", (current_user.id,))
    chats = [{"id": row[0], "title": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(chats)


@app.route("/api/chats/<int:chat_id>/messages", methods=["GET"])
@login_required
def listar_mensagens(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, current_user.id))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"erro": "Chat não encontrado"}), 404

    cursor.execute("SELECT sender, content FROM messages WHERE chat_id = %s ORDER BY created_at ASC", (chat_id,))
    mensagens = [{"sender": row[0], "content": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(mensagens)


@app.route("/api/chats/<int:chat_id>", methods=["DELETE"])
@login_required
def excluir_chat(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM chats WHERE id = %s AND user_id = %s RETURNING id",
        (chat_id, current_user.id)
    )
    chat_excluido = cursor.fetchone()
    if not chat_excluido:
        cursor.close()
        conn.close()
        return jsonify({"erro": "Chat não encontrado"}), 404

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"excluido": True})


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    chat_id = request.form.get("chat_id")
    chat_id = None if chat_id == "null" or not chat_id else int(chat_id)

    mensagem_usuario = request.form.get("mensagem", "")
    modelo_selecionado = request.form.get("modelo", "gpt-4o")

    df_enviado = None
    resumo_arquivo = ""
    file = request.files.get("file")
    if file and file.filename != '':
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            if filename.endswith('.csv'):
                df_enviado = pd.read_csv(filepath)
            elif filename.endswith(('.xlsx', '.xls')):
                df_enviado = pd.read_excel(filepath)
            if df_enviado is not None:
                resumo_arquivo = f" [Arquivo: {filename} | Colunas: {', '.join(df_enviado.columns.tolist())}]"
        except Exception:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()

    if not chat_id:
        titulo_resumido = (mensagem_usuario[:30] if mensagem_usuario else "Análise com RAG") + "..."
        cursor.execute("INSERT INTO chats (user_id, title) VALUES (%s, %s) RETURNING id",
                       (current_user.id, titulo_resumido))
        chat_id = cursor.fetchone()[0]
    else:
        cursor.execute("SELECT id FROM chats WHERE id = %s AND user_id = %s", (chat_id, current_user.id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"erro": "Acesso negado ao chat"}), 403

    display_msg = mensagem_usuario + (f" 📎 [{file.filename}]" if file and file.filename != '' else "")
    cursor.execute("INSERT INTO messages (chat_id, sender, content) VALUES (%s, %s, %s)",
                   (chat_id, "user", display_msg))
    conn.commit()

    # Salva a mensagem do usuário na memória vetorial para RAG futuro
    salvar_memoria_vetorial(current_user.id, chat_id, f"Usuário perguntou: {mensagem_usuario}{resumo_arquivo}")

    # Gera resposta utilizando RAG e modelos de IA
    resposta_ia, chart_url = gerar_resposta_llm(modelo_selecionado, mensagem_usuario, user_id=current_user.id,
                                                df=df_enviado)

    conteudo_salvo = resposta_ia
    if chart_url:
        conteudo_salvo += f"\n\n![Gráfico Gerado]({chart_url})"

    cursor.execute("INSERT INTO messages (chat_id, sender, content) VALUES (%s, %s, %s)",
                   (chat_id, "ai", conteudo_salvo))
    conn.commit()

    # Salva a resposta da IA na memória vetorial
    salvar_memoria_vetorial(current_user.id, chat_id, f"IA respondeu: {resposta_ia}")

    cursor.close()
    conn.close()

    return jsonify({"chat_id": chat_id, "resposta": resposta_ia, "chart_url": chart_url})


@app.route("/api/sheets/preencher", methods=["POST"])
@login_required
def api_preencher_sheets():
    dados = request.json
    resultado = sheets_service.preencher_tabela(
        user_id=current_user.id,
        spreadsheet_id=dados.get("spreadsheet_id"),
        range_name=dados.get("range_name", "Página1!A1"),
        values=dados.get("values", [])
    )
    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True, port=5000)