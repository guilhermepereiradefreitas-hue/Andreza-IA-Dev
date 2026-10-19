import os
import time
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from rag_service import buscar_memorias_relevantes

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _gerar_resposta_gemini(modelo, prompt):
    for tentativa in range(3):
        try:
            return gemini_client.models.generate_content(model=modelo, contents=prompt)
        except genai_errors.ServerError as erro:
            if erro.code != 503:
                raise
            if tentativa == 2:
                raise RuntimeError(
                    "O Gemini está temporariamente indisponível (erro 503). "
                    "Tente novamente em alguns minutos ou selecione outro modelo."
                ) from erro
            time.sleep(1.5 * (2 ** tentativa))


# noinspection bad-argument-type
def gerar_resposta_llm(modelo, mensagem, user_id=None, df=None):
    """Gera resposta da IA a injetar memórias de longo prazo (RAG) e dados analíticos se disponíveis."""
    try:
        contexto_rag = ""
        if user_id:
            memorias = buscar_memorias_relevantes(user_id, mensagem, limite=3)
            if memorias:
                contexto_rag = "\n\n[CONTEXTO DE CONVERSAS OU ARQUIVOS ANTERIORES - MEMÓRIA DE LONGO PRAZO]:\n" + "\n---\n".join(
                    memorias) + "\n"

        contexto_dados = ""
        if df is not None:
            resumo_estatistico = df.describe(include='all').to_string()
            contexto_dados = f"\n\n[DADOS ANALISADOS VIA PANDAS]:\nEstatísticas descritivas:\n{resumo_estatistico}\n"

        prompt_sistema = (
            "Você é a Andreza IA, uma assistente especialista em engenharia de dados, Python, "
            "análise avançada e automação de planilhas com Google Sheets. "
            "Utilize a memória de longo prazo fornecida para responder com precisão a perguntas sobre dados anteriores."
        )

        prompt_completo = prompt_sistema + contexto_rag + contexto_dados + "\n\nUsuário: " + mensagem

        if "gpt" in modelo.lower():
            response = openai_client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_completo}
                ],
                temperature=0.7
            )
            resposta_texto = response.choices[0].message.content
        elif "gemini" in modelo.lower():
            response = _gerar_resposta_gemini(modelo, prompt_completo)
            resposta_texto = response.text
        else:
            resposta_texto = f"Modelo '{modelo}' não reconhecido."

        grafico_gerado = None
        if df is not None and any(termo in mensagem.lower() for termo in
                                  ["gráfico", "plotar", "visualizar", "histograma", "barra", "dispersão"]):
            grafico_gerado = criar_grafico_automatico(df)

        return resposta_texto, grafico_gerado

    except Exception as e:
        return f"Erro ao processar com a IA: {str(e)}", None


def criar_grafico_automatico(df):
    try:
        os.makedirs("static/charts", exist_ok=True)
        filename = f"chart_{os.urandom(4).hex()}.png"
        filepath = os.path.join("static/charts", filename)

        plt.figure(figsize=(8, 4))
        sns.set_theme(style="darkgrid")

        colunas_numericas = df.select_dtypes(include=['number']).columns
        if len(colunas_numericas) >= 2:
            sns.lineplot(data=df, x=df.index, y=colunas_numericas[0])
            plt.title(f"Análise de Tendência: {colunas_numericas[0]}")
        elif len(colunas_numericas) == 1:
            sns.histplot(df[colunas_numericas[0]], kde=True, color='purple')
            plt.title(f"Distribuição de {colunas_numericas[0]}")
        else:
            plt.close()
            return None

        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        return f"/static/charts/{filename}"
    except Exception:
        return None