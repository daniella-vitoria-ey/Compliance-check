import os
import threading
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File

from src.core.monitor import Monitor
from src.core.trace_store import (
    start_trace,
    add_trace_step,
    get_trace,
    get_trace_result,
    get_last_result
)

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


@router.get("/last-result", include_in_schema=False)
def last_result():
    return get_last_result()


@router.get("/trace/{trace_id}", include_in_schema=False)
def trace_result(trace_id: str):
    trace_data = get_trace(trace_id)

    if not trace_data:
        raise HTTPException(status_code=404, detail="Trace não encontrado")

    return {
        "trace_id": trace_data["trace_id"],
        "steps": trace_data.get("agent_steps", [])
    }


@router.get("/result/{trace_id}")
def result_by_trace(trace_id: str):
    result = get_trace_result(trace_id)

    if not result:
        raise HTTPException(status_code=404, detail="Resultado não encontrado para esse trace_id")

    return result


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

        trace_id = str(uuid4())
        start_trace(trace_id=trace_id, file_path=destination, file_name=file.filename)

        add_trace_step(
            trace_id=trace_id,
            step="receive_upload",
            status="ok",
            detail=f"Arquivo recebido via API: {file.filename}"
        )

        add_trace_step(
            trace_id=trace_id,
            step="validate_file",
            status="ok",
            detail="Arquivo validado com sucesso (.txt)"
        )

        add_trace_step(
            trace_id=trace_id,
            step="save_input_document",
            status="ok",
            detail=f"Arquivo salvo em: {destination}"
        )

        add_trace_step(
            trace_id=trace_id,
            step="waiting_monitor",
            status="pending",
            detail="Arquivo aguardando processamento pelo monitor/agente"
        )

        return {
            "message": "Arquivo enviado com sucesso",
            "trace_id": trace_id,
            "status": "pending"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))