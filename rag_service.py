import os
from openai import OpenAI
from database import get_db_connection
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def gerar_embedding(texto):
    """Gera o vetor de embeddings para um determinado texto usando OpenAI."""
    try:
        response = openai_client.embeddings.create(
            input=[texto.replace("\n", " ")],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return None


def salvar_memoria_vetorial(user_id, chat_id, texto):
    """Salva um trecho de texto e o seu respetivo vetor no PostgreSQL."""
    vetor = gerar_embedding(texto)
    if not vetor:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO document_embeddings (user_id, chat_id, content, embedding) VALUES (%s, %s, %s, %s)",
        (user_id, chat_id, texto, vetor)
    )
    conn.commit()
    cursor.close()
    conn.close()


def buscar_memorias_relevantes(user_id, query, limite=3):
    """Busca as memórias passadas mais similares à pergunta atual usando distância vetorial (<=>)."""
    vetor_query = gerar_embedding(query)
    if not vetor_query:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    # Utiliza o operador de distância cosseno do pgvector (<=>)
    cursor.execute("""
                   SELECT content
                   FROM document_embeddings
                   WHERE user_id = %s
                   ORDER BY embedding <=> %s::vector
                       LIMIT %s;
                   """, (user_id, str(vetor_query), limite))

    resultados = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return resultados