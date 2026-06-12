import os
import threading
from fastapi import APIRouter, HTTPException, UploadFile, File

from src.core.monitor import Monitor
from src.core.agent_status import load_agent_status

router = APIRouter(prefix="/agent", tags=["agent"])

monitor = Monitor()
monitor_thread = None

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
INPUT_DIR = os.path.join(BASE_DIR, "data", "input")


@router.post("/start-monitor")
def start_monitor():
    global monitor_thread

    if monitor.is_running():
        return {
            "message": "Monitor já está em execução",
            "status": "running"
        }

    monitor_thread = threading.Thread(target=monitor.run, daemon=True)
    monitor_thread.start()

    return {
        "message": "Monitor iniciado com sucesso",
        "status": "running"
    }


@router.post("/stop-monitor")
def stop_monitor():
    if not monitor.is_running():
        return {
            "message": "Monitor já está parado",
            "status": "stopped"
        }

    monitor.stop()

    return {
        "message": "Solicitação de parada enviada",
        "status": "stopping"
    }


@router.get("/status")
def monitor_status():
    return {
        "status": "running" if monitor.is_running() else "stopped"
    }


@router.get("/last-result")
def last_result():
    return load_agent_status()


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    try:
        os.makedirs(INPUT_DIR, exist_ok=True)

        if not file.filename.endswith(".txt"):
            raise HTTPException(
                status_code=400,
                detail="Apenas arquivos .txt são permitidos."
            )

        destination = os.path.join(INPUT_DIR, file.filename)
        content = await file.read()

        with open(destination, "wb") as f:
            f.write(content)

        return {
            "message": "Arquivo enviado com sucesso",
            "file_path": destination
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))