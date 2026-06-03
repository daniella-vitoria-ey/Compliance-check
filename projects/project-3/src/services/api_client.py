import requests
from src.core.logger import get_logger

logger = get_logger(__name__)

class APIClient:

    def analyze(self, text: str):
        logger.info("Chamando API de análise")

        response = requests.post(
            "http://localhost:8000/analyze",
            json={"text_to_analyze": text}
        )

        if response.status_code != 200:
            logger.error(f"Erro na API: {response.text}")

        response.raise_for_status()

        return response.json()