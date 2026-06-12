from src.core.llm_client import analyze_with_ai
import json

# Função que recebe o texto, chama a IA para análise e processa a resposta (separa a lógica de análise do restante da aplicação, facilitando testes e manutenção)
def analyze_text(text: str) -> dict:
    
    # Envia o texto para a IA e recebe a resposta (utiliza a função definida no cliente de IA para obter a análise)
    ai_response = analyze_with_ai(text)

    try:
        result = json.loads(ai_response)
        return result
    except Exception as e:
        return {
            "is_compliant": False,
            "reason": "Erro ao interpretar resposta da IA",
            "mentioned_products": []
        }