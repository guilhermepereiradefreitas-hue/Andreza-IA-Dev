import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Habilita a extensão pgvector no PostgreSQL (ela precisa estar instalada no servidor).
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    except psycopg2.errors.FeatureNotSupported as exc:
        cursor.close()
        conn.close()
        raise RuntimeError(
            "A extensão pgvector não está instalada no servidor PostgreSQL. "
            "Instale o pgvector no servidor e execute novamente."
        ) from exc

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       username
                       VARCHAR
                   (
                       100
                   ) UNIQUE NOT NULL,
                       password_hash VARCHAR
                   (
                       255
                   ) NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       );
                   CREATE TABLE IF NOT EXISTS google_tokens
                   (
                       user_id
                       INTEGER
                       PRIMARY
                       KEY
                       REFERENCES
                       users
                   (
                       id
                   ) ON DELETE CASCADE,
                       token_data TEXT NOT NULL,
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       );
                   CREATE TABLE IF NOT EXISTS chats
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       user_id
                       INTEGER
                       REFERENCES
                       users
                   (
                       id
                   ) ON DELETE CASCADE,
                       title VARCHAR
                   (
                       255
                   ) NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       );
                   CREATE TABLE IF NOT EXISTS messages
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       chat_id
                       INTEGER
                       REFERENCES
                       chats
                   (
                       id
                   ) ON DELETE CASCADE,
                       sender VARCHAR
                   (
                       50
                   ) NOT NULL,
                       content TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       );
                   -- Tabela de memória vetorial (RAG) para embeddings de 1536 dimensões (text-embedding-3-small)
                   CREATE TABLE IF NOT EXISTS document_embeddings
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY,
                       user_id
                       INTEGER
                       REFERENCES
                       users
                   (
                       id
                   ) ON DELETE CASCADE,
                       chat_id INTEGER REFERENCES chats
                   (
                       id
                   )
                     ON DELETE CASCADE,
                       content TEXT NOT NULL,
                       embedding vector
                   (
                       1536
                   ),
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       );
                   """)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Banco de dados PostgreSQL com suporte a RAG (pgvector) inicializado com sucesso!")