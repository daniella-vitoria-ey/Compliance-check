import os
import threading
from copy import deepcopy
from typing import Any, Dict, Optional

_TRACE_LOCK = threading.Lock()
TRACE_STORE: Dict[str, Dict[str, Any]] = {}
LAST_TRACE_ID: Optional[str] = None


def start_trace(
    trace_id: str,
    file_path: str,
    file_name: Optional[str] = None
) -> None:
    global LAST_TRACE_ID

    with _TRACE_LOCK:
        TRACE_STORE[trace_id] = {
            "trace_id": trace_id,
            "file_path": os.path.abspath(file_path),
            "last_file": file_name or os.path.basename(file_path),
            "status": "pending",
            "destination": None,
            "reason": None,
            "result": None,
            "agent_steps": []
        }
        LAST_TRACE_ID = trace_id


def add_trace_step(
    trace_id: str,
    step: str,
    status: str,
    detail: str,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    with _TRACE_LOCK:
        if trace_id not in TRACE_STORE:
            TRACE_STORE[trace_id] = {
                "trace_id": trace_id,
                "file_path": None,
                "last_file": None,
                "status": "pending",
                "destination": None,
                "reason": None,
                "result": None,
                "agent_steps": []
            }

        item = {
            "step": step,
            "status": status,
            "detail": detail
        }

        if extra:
            item["extra"] = extra

        TRACE_STORE[trace_id]["agent_steps"].append(item)


def update_trace_result(
    trace_id: str,
    status: Optional[str] = None,
    destination: Optional[str] = None,
    reason: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
    last_file: Optional[str] = None
) -> None:
    global LAST_TRACE_ID

    with _TRACE_LOCK:
        if trace_id not in TRACE_STORE:
            TRACE_STORE[trace_id] = {
                "trace_id": trace_id,
                "file_path": None,
                "last_file": None,
                "status": "pending",
                "destination": None,
                "reason": None,
                "result": None,
                "agent_steps": []
            }

        if status is not None:
            TRACE_STORE[trace_id]["status"] = status

        if destination is not None:
            TRACE_STORE[trace_id]["destination"] = destination

        if reason is not None:
            TRACE_STORE[trace_id]["reason"] = reason

        if result is not None:
            TRACE_STORE[trace_id]["result"] = result

        if last_file is not None:
            TRACE_STORE[trace_id]["last_file"] = last_file

        LAST_TRACE_ID = trace_id


def get_trace(trace_id: str) -> Optional[Dict[str, Any]]:
    with _TRACE_LOCK:
        data = TRACE_STORE.get(trace_id)
        return deepcopy(data) if data else None


def get_trace_result(trace_id: str) -> Optional[Dict[str, Any]]:
    with _TRACE_LOCK:
        data = TRACE_STORE.get(trace_id)
        if not data:
            return None

        return deepcopy({
            "trace_id": data.get("trace_id"),
            "last_file": data.get("last_file"),
            "status": data.get("status"),
            "destination": data.get("destination"),
            "reason": data.get("reason"),
            "result": data.get("result"),
            "agent_steps": data.get("agent_steps", [])
        })


def get_last_result() -> Dict[str, Any]:
    with _TRACE_LOCK:
        if not LAST_TRACE_ID or LAST_TRACE_ID not in TRACE_STORE:
            return {
                "trace_id": None,
                "last_file": None,
                "status": "idle",
                "destination": None,
                "reason": None,
                "result": None,
                "agent_steps": []
            }

        data = TRACE_STORE[LAST_TRACE_ID]
        return deepcopy({
            "trace_id": data.get("trace_id"),
            "last_file": data.get("last_file"),
            "status": data.get("status"),
            "destination": data.get("destination"),
            "reason": data.get("reason"),
            "result": data.get("result"),
            "agent_steps": data.get("agent_steps", [])
        })


def find_trace_id_by_file_path(file_path: str) -> Optional[str]:
    target = os.path.abspath(file_path)

    with _TRACE_LOCK:
        for trace_id, trace_data in TRACE_STORE.items():
            stored_path = trace_data.get("file_path")
            if stored_path and os.path.abspath(stored_path) == target:
                return trace_id

    return None