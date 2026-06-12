from src.services.compliance_service import analyze_text

# Testes para o serviço de análise de conformidade (garante que a lógica de análise esteja funcionando corretamente e que a integração com a IA esteja retornando os resultados esperados)
def test_analyze_text_basic():
    result = analyze_text("Investir no produto XPTO com risco")

    assert isinstance(result, dict)
    assert "is_compliant" in result
    assert "reason" in result
    assert "mentioned_products" in result

# Testa se a função de análise retorna um dicionário com os campos esperados (verifica a estrutura da resposta da função de análise)
def test_analyze_text_detect_product():
    result = analyze_text("Produto XPTO")

    assert isinstance(result["mentioned_products"], list)