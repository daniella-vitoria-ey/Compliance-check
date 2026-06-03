import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.agents.agent import ComplianceAgent
from src.core.logger import get_logger

logger = get_logger(__name__)


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

        self.agent.process(file_path)


class Monitor:

    def __init__(self, path="data/input"):
        self.path = path
        self.observer = Observer()

    def run(self):
        os.makedirs(self.path, exist_ok=True)

        handler = Handler()
        self.observer.schedule(handler, self.path, recursive=False)

        logger.info(f"Monitorando pasta: {self.path}")

        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Parando monitor")
            self.observer.stop()

        self.observer.join()