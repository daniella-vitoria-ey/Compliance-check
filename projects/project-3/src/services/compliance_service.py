import ast
import json
import re
from src.core.llm_client import analyze_with_ai
from src.rag.retrieval import retrieve
from src.rag.reranker import rerank

PRODUCT_CATALOG = {
    "criptomoedas": ["criptomoeda", "criptomoedas", "bitcoin", "ethereum", "criptoativo", "criptoativos"],
    "ações": ["ação", "ações", "renda variável", "small caps", "blue chips"],
    "derivativos": ["derivativo", "derivativos", "opção", "opções", "futuros"],
    "cdb": ["cdb", "cdbs"],
    "tesouro direto": ["tesouro direto", "tesouro selic"],
    "fundos multimercado": ["fundo multimercado", "fundos multimercado", "multimercado"],
    "fundos de ações": ["fundo de ações", "fundos de ações"],
    "cri/cra": ["cri", "cra"],
    "lci/lca": ["lci", "lca"],
    "coe": ["coe"]
}

def extract_products_fallback(text: str) -> list[str]:
    text_lower = text.lower()
    found = []

    for canonical_name, aliases in PRODUCT_CATALOG.items():
        if any(alias in text_lower for alias in aliases):
            found.append(canonical_name)

    return found

def clean_reason(reason: str) -> str:
    if not isinstance(reason, str):
        return "Justificativa não fornecida pelo modelo."

    cleaned = reason.strip()
    cleaned = re.sub(r"^\s*is_compliant\s*:\s*(true|false)\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^\s*reason\s*:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = " ".join(cleaned.split())

    return cleaned if cleaned else "Justificativa não fornecida pelo modelo."

def parse_llm_response(raw_response: str) -> dict:
    if not raw_response or not isinstance(raw_response, str):
        return {}

    cleaned = raw_response.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    candidates = [cleaned]

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        candidates.append(match.group(0))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        try:
            parsed = ast.literal_eval(candidate)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    return {}

def analyze_text(text: str, client_profile: str) -> dict:
    docs = retrieve(text)
    docs = rerank(text, docs)

    context = "\n\n".join(
        [
            f"Documento: {d['source']}\nChunk: {d['chunk_id']}\nTexto: {d['text']}"
            for d in docs
        ]
    )

    prompt = f"""
Você é um especialista em compliance financeiro.

Sua tarefa é analisar o TEXTO DO USUÁRIO considerando o PERFIL DO CLIENTE e usando SOMENTE o CONTEXTO recuperado.

REGRAS OBRIGATÓRIAS:
- Use apenas as informações presentes no CONTEXTO.
- Não use conhecimento externo.
- Considere explicitamente o perfil do cliente ao avaliar adequação.
- Se não houver evidência suficiente no CONTEXTO, diga isso claramente.
- Responda SOMENTE com JSON válido.
- Não escreva nada antes ou depois do JSON.

Formato obrigatório:
{{
  "is_compliant": true,
  "reason": "explicação objetiva baseada no contexto recuperado e no perfil do cliente",
  "mentioned_products": ["lista de produtos citados no texto"]
}}

PERFIL DO CLIENTE:
{client_profile}

CONTEXTO:
{context}

TEXTO A ANALISAR:
{text}
"""

    llm_result = analyze_with_ai(prompt)
    raw_response = llm_result["content"]
    usage = llm_result["usage"]

    parsed = parse_llm_response(raw_response)

    is_compliant = parsed.get("is_compliant", False)
    if not isinstance(is_compliant, bool):
        if isinstance(is_compliant, str):
            is_compliant = is_compliant.strip().lower() == "true"
        else:
            is_compliant = False

    reason = clean_reason(parsed.get("reason", raw_response))

    mentioned_products = parsed.get("mentioned_products", [])
    if not isinstance(mentioned_products, list) or not mentioned_products:
        mentioned_products = extract_products_fallback(text)

    return {
        "is_compliant": is_compliant,
        "reason": reason,
        "mentioned_products": mentioned_products,
        "sources": [
            {
                "source_document": d["source"],
                "source_chunk_id": d["chunk_id"]
            }
            for d in docs
        ],
        "usage": usage
    }