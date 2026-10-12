# 🚀 Documentação Oficial - Andreza IA

Bem-vindo à documentação oficial da **Andreza IA**, uma plataforma corporativa avançada de assistência em análise de dados, processamento de planilhas (Excel/CSV), automação via Google Sheets e geração de gráficos analíticos em tempo real utilizando modelos de linguagem de ponta (OpenAI GPT-4o e Google Gemini).

## 📑 Índice

1. [Histórico de Versões](#1-histórico-de-versões)

2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)

3. [Guia de Instalação e Configuração](#3-guia-de-instalação-e-configuração)

4. [Manual do Usuário](#4-manual-do-usuário)

5. [Endpoints da API](#5-endpoints-da-api)

## 1. Histórico de Versões

### 🟢 Versão 1.3.0 (Atual - Outubro de 2026)

* **Novidades:**

  * **Análise Avançada com Gráficos Automáticos:** Integração com bibliotecas Python (`matplotlib` e `seaborn`) para gerar gráficos analíticos estáticos (`.png`) instantaneamente no chat a partir do upload de arquivos.

  * **Motor de Contexto Estatístico:** O Pandas extrai descrições estatísticas completas e passa como contexto para a IA antes da inferência.

* **Correções e Melhorias:**

  * Tratamento de concorrência e renderização de imagens diretamente no DOM do chat em JavaScript.

### 🟡 Versão 1.2.0

* **Novidades:**

  * Suporte a **Upload de Arquivos** de planilhas (`.csv`, `.xlsx`, `.xls`).

  * Extração automatizada de dimensões, nomes de colunas e primeiras linhas pelo backend.

  * Indicadores visuais dinâmicos de arquivos selecionados na interface.

### 🟠 Versão 1.1.0

* **Novidades:**

  * Integração com a **API do Google Sheets** (`GoogleSheetsService`) para leitura e escrita automatizada em planilhas na nuvem.

  * Alternância dinâmica de modelos de IA na interface (`GPT-4o` e `Gemini 1.5 Pro`).

### 🔴 Versão 1.0.0 (Lançamento Inicial)

* **Novidades:**

  * Estrutura base em Flask com autenticação de usuários (`Flask-Login`, `Flask-Bcrypt`).

  * Persistência de chats e histórico de mensagens em banco de dados **PostgreSQL**.

  * Interface moderna estilo ChatGPT no front-end.

## 2. Arquitetura do Sistema

A CodeFusion IA adota uma arquitetura monolítica modular e segura:

* **Front-end:** HTML5, CSS3 Customizado, JavaScript Vanilla e FontAwesome.

* **Back-end:** Python com Flask framework.

* **Camada de Dados & Análise:** Pandas, OpenPyXL, Matplotlib e Seaborn.

* **Banco de Dados:** PostgreSQL relacional (`users`, `chats`, `messages`).

* **Serviços Externos:** OpenAI API, Google Generative AI API e Google Sheets API.

## 3. Guia de Instalação e Configuração

### Pré-requisitos

* Python 3.10 ou superior instalado.

* PostgreSQL instalado e configurado localmente ou em nuvem.

### Passo a Passo

1. **Clone ou abra a pasta do projeto e crie o ambiente virtual:**

   ```
   python -m venv venv
   venv\Scripts\activate   # No Windows
   source venv/bin/activate # No Linux/macOS
   
   ```

2. **Instale as dependências contidas no `requirements.txt`:**

   ```
   pip install -r requirements.txt
   
   ```

3. **Configure as Variáveis de Ambiente (`.env`):**
   Crie um arquivo `.env` na raiz com o seguinte conteúdo:

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=assistente_db
   DB_USER=postgres
   DB_PASSWORD=sua_senha_postgres
   SECRET_KEY=sua_chave_secreta_super_segura
   OPENAI_API_KEY=sua_chave_openai_aqui
   GEMINI_API_KEY=sua_chave_gemini_aqui
   
   ```

4. **Inicialize o Banco de Dados:**

   ```
   python database.py
   
   ```

5. **Execute a Aplicação:**

   ```
   python app.py
   
   ```

   Acesse a aplicação em `http://localhost:5000` no seu navegador.

## 4. Manual do Usuário

### A. Autenticação

* **Registro:** Acesse `/register` para criar uma nova conta de usuário (as senhas são criptografadas com Bcrypt).

* **Login:** Acesse `/login` com suas credenciais para entrar no sistema.

### B. Iniciando uma Conversa e Usando o Chat

* Na tela principal, você verá uma barra lateral com seu histórico de chats salvos e a opção **"+ Novo Chat"**.

* No topo da área de chat, você pode alternar o modelo de inteligência artificial desejado (`GPT-4o` ou `Gemini 1.5 Pro`).

### C. Como Anexar e Analisar Planilhas

1. Clique no ícone de **clipe de papel** (`📎`) localizado na barra inferior de digitação.

2. Selecione um arquivo compatível (`.csv`, `.xlsx` ou `.xls`).

3. Um indicador verde mostrará o nome do arquivo carregado.

4. Digite sua pergunta (ex: *"Analise os dados e gere um gráfico de tendência"* ou *"Quais são os principais insights desta planilha?"*).

5. Pressione **Enviar** ou tecle `Enter`. A IA processará os dados estatísticos via Pandas, gerará gráficos analíticos automáticos (quando solicitado) e exibirá tudo diretamente no histórico do chat.

### D. Integração com o Google Sheets

* O sistema possui endpoints dedicados para comunicação com planilhas do Google Cloud via credenciais de serviço, permitindo a automação do preenchimento de células programaticamente.

## 5. Endpoints da API

| Rota | Método | Descrição | 
| ----- | ----- | ----- | 
| `/login` | GET/POST | Autenticação do usuário | 
| `/register` | GET/POST | Cadastro de novo usuário | 
| `/logout` | GET | Encerra a sessão ativa | 
| `/` | GET | Interface principal do chat | 
| `/api/chats` | GET | Retorna lista de chats do usuário logado | 
| `/api/chats/<id>/messages` | GET | Retorna o histórico de mensagens de um chat específico | 
| `/api/chat` | POST | Envia mensagem e opcionalmente arquivo para processamento da IA | 
| `/api/sheets/preencher` | POST | Automatiza o preenchimento de tabelas no Google Sheets | 
