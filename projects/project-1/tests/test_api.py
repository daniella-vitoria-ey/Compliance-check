from fastapi.testclient import TestClient
from src.main import app

# Cria um cliente de teste para a aplicação FastAPI (permite simular requisições HTTP para os endpoints da API durante os testes)
client = TestClient(app)

# Testa o endpoint de análise com um texto válido (verifica se a API retorna a resposta esperada para uma entrada correta)
def test_analyze_endpoint():
    response = client.post(
        "/analyze",
        json={"text_to_analyze": "Investir no produto XPTO com risco"}
    )

    assert response.status_code == 200

    data = response.json()

# Verifica se a resposta contém os campos esperados (garante que a estrutura da resposta esteja correta)
    assert "is_compliant" in data
    assert "reason" in data
    assert "mentioned_products" in data

# Testa o endpoint de análise com um texto muito curto (verifica se a validação de entrada está funcionando corretamente e retorna o erro esperado)
def test_analyze_validation():
    response = client.post(
        "/analyze",
        json={"text_to_analyze": "curto"}
    )

    assert response.status_code == 422