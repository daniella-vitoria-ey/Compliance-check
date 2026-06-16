import os
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.agents.agent import ComplianceAgent
from src.core.agent_status import load_agent_status
from src.core.logger import get_logger
from src.core.trace_store import find_trace_id_by_file_path, add_trace_step

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

        trace_id = find_trace_id_by_file_path(file_path)

        if trace_id:
            add_trace_step(
                trace_id=trace_id,
                step="monitor_detected_file",
                status="ok",
                detail=f"Monitor detectou o arquivo: {os.path.basename(file_path)}"
            )

            add_trace_step(
                trace_id=trace_id,
                step="start_processing",
                status="ok",
                detail="Monitor iniciou o processamento do documento"
            )

        try:
            self.agent.process(file_path)

            status_data = load_agent_status()

            if trace_id and isinstance(status_data, dict):
                result = status_data.get("result", {})
                final_status = status_data.get("status", "unknown")
                destination = status_data.get("destination")
                reason = status_data.get("reason", "Execução finalizada")

                analyze_detail = "Análise de conformidade executada com sucesso"

                if isinstance(result, dict):
                    is_compliant = result.get("is_compliant")
                    if is_compliant is True:
                        analyze_detail = "Análise concluída com resultado compatível"
                    elif is_compliant is False:
                        analyze_detail = "Análise concluída com necessidade de revisão"

                add_trace_step(
                    trace_id=trace_id,
                    step="analyze_recommendation",
                    status="ok",
                    detail=analyze_detail
                )

                if destination:
                    add_trace_step(
                        trace_id=trace_id,
                        step="route_document",
                        status=final_status,
                        detail=f"Documento direcionado para: {destination}"
                    )

                add_trace_step(
                    trace_id=trace_id,
                    step="finish",
                    status=final_status,
                    detail=reason
                )

        except Exception as e:
            logger.exception(f"Erro inesperado ao processar {file_path}: {str(e)}")

            if trace_id:
                add_trace_step(
                    trace_id=trace_id,
                    step="processing_error",
                    status="error",
                    detail=str(e)
                )


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