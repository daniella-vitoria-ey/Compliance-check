import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.agents.agent import ComplianceAgent
from src.core.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_DIR = os.path.join(BASE_DIR, "data", "input")
APPROVED_DIR = os.path.join(BASE_DIR, "data", "output", "approved")
REVIEW_DIR = os.path.join(BASE_DIR, "data", "output", "rejected_for_review")

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.agent = ComplianceAgent()

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        if file_path.endswith(".gitkeep"):
            return

        time.sleep(0.5)

        if not os.path.exists(file_path):
            return

        logger.info(f"Novo arquivo detectado: {file_path}")

        try:
            self.agent.process(file_path)
        except Exception as e:
            logger.exception(f"Erro inesperado ao processar {file_path}: {str(e)}")

class Monitor:
    def __init__(self, path=INPUT_DIR):
        self.path = path
        self.observer = None
        self._running = False

    def run(self):
        if self._running:
            logger.info("Monitor já está em execução")
            return

        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(APPROVED_DIR, exist_ok=True)
        os.makedirs(REVIEW_DIR, exist_ok=True)

        self.observer = Observer()
        handler = Handler()
        self.observer.schedule(handler, self.path, recursive=False)

        logger.info(f"Monitorando pasta: {self.path}")

        self.observer.start()
        self._running = True

        try:
            while self._running:
                time.sleep(1)
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            self._running = False
            logger.info("Monitor finalizado")

    def stop(self):
        logger.info("Solicitação para parar monitor recebida")
        self._running = False

    def is_running(self):
        return self._running