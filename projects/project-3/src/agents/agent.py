from src.core.logger import get_logger
from src.services.api_client import APIClient
from src.core.file_manager import FileManager

logger = get_logger(__name__)


# Estado do documento (estilo LangGraph)
class DocumentState:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = None
        self.result = None
        self.destination = None


class ComplianceAgent:

    def __init__(self):
        self.api = APIClient()
        self.files = FileManager()

    def process(self, file_path: str):
        logger.info(f"Iniciando processamento: {file_path}")

        state = DocumentState(file_path)

        try:
            state = self.read_file(state)
            state = self.validate_content(state)
            state = self.analyze(state)
            state = self.decide(state)
            state = self.act(state)

            logger.info("Processamento finalizado com sucesso")

        except Exception as e:
            logger.error(f"Erro no processamento: {e}")

    # Etapas do pipeline

    def read_file(self, state):
        logger.info("Lendo arquivo")

        with open(state.file_path, "r") as f:
            state.content = f.read()

        return state

    def validate_content(self, state):
        logger.info("Validando conteúdo")

        if not state.content or not state.content.strip():
            logger.warning("Arquivo vazio - ignorando")
            raise ValueError("Empty file")

        return state

    def analyze(self, state):
        logger.info("Enviando conteúdo para API")

        state.result = self.api.analyze(state.content)

        logger.info(f"Resultado da API: {state.result}")

        return state

    def decide(self, state):
        logger.info("Tomando decisão")

        is_compliant = state.result.get("is_compliant", False)

        if is_compliant:
            state.destination = "data/output/approved"
            logger.info("Documento aprovado")
        else:
            state.destination = "data/output/rejected_for_review"
            logger.warning("Documento não conforme")

        return state

    def act(self, state):
        logger.info("Executando ação")

        self.files.move(state.file_path, state.destination)

        if "rejected_for_review" in state.destination:
            logger.warning(f"🚨 Alerta: {state.file_path} precisa revisão")

        return state