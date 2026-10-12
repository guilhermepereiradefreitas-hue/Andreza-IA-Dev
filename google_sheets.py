import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from database import get_db_connection

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.readonly']

class GoogleSheetsUserService:
    def __init__(self, credentials_path="credentials.json"):
        self.credentials_path = credentials_path

    def criar_fluxo_autorizacao(self, redirect_uri):
        """Cria o fluxo OAuth2 para o usuário autorizar o acesso ao Google."""
        return Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )

    def salvar_token_usuario(self, user_id, credentials):
        """Salva o token OAuth do usuário no PostgreSQL."""
        token_json = credentials.to_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO google_tokens (user_id, token_data, updated_at) 
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) 
            DO UPDATE SET token_data = EXCLUDED.token_data, updated_at = CURRENT_TIMESTAMP;
        """, (user_id, token_json))
        conn.commit()
        cursor.close()
        conn.close()

    def obter_credenciais_usuario(self, user_id):
        """Recupera e valida as credenciais do Google do usuário armazenadas no banco."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT token_data FROM google_tokens WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return None

        token_data = json.loads(row[0])
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)

        # Atualiza o token se estiver expirado
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            self.salvar_token_usuario(user_id, creds)

        return creds

    def preencher_tabela(self, user_id, spreadsheet_id, range_name, values):
        """Preenche dados na planilha utilizando as credenciais específicas do usuário logado."""
        creds = self.obter_credenciais_usuario(user_id)
        if not creds:
            return {"status": "erro", "mensagem": "Conta Google não conectada. Por favor, vincule sua conta nas configurações."}

        try:
            service = build('sheets', 'v4', credentials=creds)
            body = {'values': values}
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return {"status": "sucesso", "atualizacoes": result.get('updates')}
        except Exception as e:
            return {"status": "erro", "mensagem": str(e)}