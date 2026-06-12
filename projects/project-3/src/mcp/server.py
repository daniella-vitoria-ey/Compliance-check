import json
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

from src.core.file_manager import FileManager
from src.core.logger import get_logger
from src.core.metrics import load_metrics

load_dotenv()

logger = get_logger(__name__)
file_manager = FileManager()

mcp = FastMCP("Compliance MCP Server")

API_URL = "http://127.0.0.1:8000/analyze"

@mcp.tool
def analyze_recommendation(text: str, client_profile: str) -> dict:
    logger.info("MCP Tool: analyze_recommendation")

    payload = {
        "text_to_analyze": text,
        "client_profile": client_profile
    }

    response = httpx.post(API_URL, json=payload, timeout=60.0)
    response.raise_for_status()

    return response.json()

@mcp.tool
def move_document(source: str, destination: str) -> dict:
    logger.info(f"MCP Tool: move_document | {source} -> {destination}")
    file_manager.move(source, destination)

    return {
        "success": True,
        "source": source,
        "destination": destination
    }

@mcp.tool
def create_alert(message: str) -> dict:
    logger.warning(f"MCP Tool: create_alert | {message}")

    return {
        "success": True,
        "message": message
    }

@mcp.resource("metrics://automation")
def automation_metrics() -> str:
    metrics = load_metrics()
    return json.dumps(metrics, ensure_ascii=False, indent=2)

@mcp.prompt
def compliance_review_prompt(text: str, client_profile: str) -> str:
    return f"""
Você é um analista de compliance do setor financeiro.

Avalie a recomendação abaixo considerando o perfil do cliente.

Perfil do cliente: {client_profile}

Texto da recomendação:
{text}

Responda com foco em:
1. adequação ao perfil do cliente
2. linguagem inadequada ou promessas indevidas
3. risco dos produtos mencionados
4. necessidade de revisão manual
""".strip()

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)