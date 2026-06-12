import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# carrega variáveis do .env
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
# Configura o cliente para se conectar ao Azure OpenAI usando as variáveis de ambiente (separa a configuração da lógica de negócio, facilitando manutenção e segurança)
def analyze_with_ai(text: str) -> str:

    # PROMPT definido para orientar a análise da IA
    prompt = f"""
    Você é um especialista em compliance financeiro com foco em análise de recomendações de investimento.

    OBJETIVO:
    Avaliar se o texto está em conformidade com boas práticas de mercado.

    CRITÉRIOS:
    - Promessas de lucro garantido → NÃO compliant
    - Ausência de risco → NÃO compliant
    - Linguagem equilibrada → compliant

    INSTRUÇÕES:
    - Analise o texto de forma contextual
    - Não baseie a decisão apenas em palavras isoladas
    - Seja consistente

    FORMATO:
    Responda SOMENTE com JSON válido:

    {{
      "is_compliant": true,
      "reason": "explicação clara",
      "mentioned_products": ["lista"]
    }}

    TEXTO:
    \"\"\"{text}\"\"\"
    """
# Envia o prompt para a IA e recebe a resposta (utiliza o cliente configurado para obter a análise da IA com base no prompt definido)
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content