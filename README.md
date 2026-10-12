# 🤖 Andreza IA

**Andreza IA** é uma aplicação web profissional de Inteligência Artificial desenvolvida em Python (Flask) inspirada na interface do ChatGPT. Ela foi projetada especialmente para **análise avançada de dados**, processamento de arquivos CSV/Excel, **geração automática de gráficos**, **memória de longo prazo (RAG com pgvector)** e **automação e preenchimento de planilhas via Google Sheets API (com OAuth2 por usuário)**.

---

## 🚀 Funcionalidades Principais

- **Interface Moderna (Dark Mode)**: Layout idêntico ao ChatGPT, com barra lateral de navegação e seletor de modelos.
- **Autenticação Segura**: Sistema de login e cadastro de usuários com senhas criptografadas (`Flask-Bcrypt`).
- **Troca Dinâmica de Modelos de LLM**: Alterne instantaneamente entre **GPT-4o (OpenAI)** e **Gemini 1.5 Pro (Google)** diretamente na interface.
- **Histórico Dinâmico de Chats**: Suporte completo para criar novos chats, alternar conversas e salvar todo o histórico no **PostgreSQL**.
- **Upload e Análise Avançada de Dados**: Envie arquivos `.csv`, `.xlsx` ou `.xls` para que o Pandas faça resumos estatísticos automáticos e a IA responda baseada nos dados.
- **Geração de Gráficos Analíticos**: A IA detecta pedidos de visualização e gera gráficos dinâmicos (`.png`) direto na tela do chat.
- **Automação Google Sheets (OAuth2 Individual)**: Cada usuário pode conectar sua própria conta Google para ler e preencher planilhas no seu Google Drive pessoal.
- **Memória de Longo Prazo (RAG com pgvector)**: Vetorização semântica de conversas e arquivos passados usando a extensão `pgvector` do PostgreSQL e embeddings da OpenAI (`text-embedding-3-small`).

---

## 📁 Estrutura do Projeto

```text
chatgpt-assistente-dados/
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── img/
│   │   └── logo.png  <-- (Coloque sua logo aqui)
│   └── charts/       <-- (Gráficos gerados automaticamente)
│
├── templates/
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── uploads/          <-- (Planilhas enviadas temporariamente)
├── .env
├── requirements.txt
├── database.py
├── rag_service.py
├── llm_service.py
├── google_sheets.py
├── app.py
└── README.md

🛠️ Passo a Passo de Instalação e Execução
1. Pré-requisitos
Python 3.10+ instalado.

PostgreSQL instalado e rodando na sua máquina.

2. Clonar ou Criar a Pasta do Projeto
Abra o seu terminal na pasta do projeto e crie um ambiente virtual:

``bash
python -m venv venv
venv\Scripts\activate  # No Windows
source venv/bin/activate  # No Linux/Mac
```bash

3. Instalar as Dependências
Instalaremos todas as bibliotecas necessárias (Flask, Pandas, OpenAI, Google GenAI, pgvector, etc.):

```bash
pip install -r requirements.txt

4. Configurar as Variáveis de Ambiente (.env)
Crie um arquivo chamado .env na raiz do projeto e preencha com as suas chaves e dados:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=assistente_db
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres
SECRET_KEY=sua_chave_secreta_super_segura
OPENAI_API_KEY=sua_chave_da_openai_aqui
GEMINI_API_KEY=sua_chave_do_gemini_aqui
```bash

5. Como Ativar e Testar o Banco Vetorial (pgvector)
Certifique-se de ter instalado a extensão vector no seu PostgreSQL (se usar PostgreSQL local, abra o psql ou pgAdmin e execute CREATE EXTENSION vector; no banco assistente_db).

Instale as dependências: pip install -r requirements.txt.

Rode o script de banco de dados para criar as tabelas e ativar o suporte vetorial:

```bash
python database.py  
```bash

6. Configurar o Google Cloud (Opcional para Google Sheets)
Acesse o Google Cloud Console.

Ative a Google Sheets API e a Google Drive API.

Crie credenciais do tipo OAuth 2.0 (Aplicativo para Computador).

Baixe o arquivo JSON de credenciais, renomeie para credentials.json e coloque na raiz do projeto.

Na barra lateral da aplicação web, clique em "Conectar Conta Google" para vincular o seu usuário via OAuth.

7. Executar a Aplicação

No terminal, execute o seguinte comando para iniciar a aplicação:

```bash
python app.py 

8. Acessar a Aplicação
Abra o navegador em: http://localhost:5000

📖 Manual de Uso
Login / Cadastro: Ao acessar pela primeira vez, crie sua conta ou faça login.

Nova Conversa: Clique em "Novo Chat" na barra lateral para iniciar um novo tópico (o título será gerado automaticamente).

Seleção de Modelo: No topo da tela, escolha entre GPT-4o e Gemini 1.5 Pro conforme sua preferência.

Envio de Planilhas e Gráficos: Clique no ícone de clipe de papel (📎) na caixa de texto, envie um arquivo .csv ou .xlsx e digite comandos como: "Analise os dados e gere um gráfico de tendência".

Memória RAG: Pergunte à IA sobre conteúdos enviados em conversas ou planilhas anteriores; ela buscará o contexto vetorial automaticamente.

Desenvolvido com dedicação por Guilherme Pereira de Freitas ( Andreza IA ) - 2026.
