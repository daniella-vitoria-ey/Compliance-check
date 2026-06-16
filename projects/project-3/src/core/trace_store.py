import os
from typing import Any, Dict, Optional

TRACE_STORE: Dict[str, Dict[str, Any]] = {}


def start_trace(trace_id: str, file_path: str) -> None:
    TRACE_STORE[trace_id] = {
        "trace_id": trace_id,
        "file_path": os.path.abspath(file_path),
        "steps": []
    }


def add_trace_step(
    trace_id: str,
    step: str,
    status: str,
    detail: str,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    if trace_id not in TRACE_STORE:
        TRACE_STORE[trace_id] = {
            "trace_id": trace_id,
            "file_path": None,
            "steps": []
        }

    item = {
        "step": step,
        "status": status,
        "detail": detail
    }

    if extra:
        item["extra"] = extra

    TRACE_STORE[trace_id]["steps"].append(item)


def get_trace(trace_id: str) -> Optional[Dict[str, Any]]:
    return TRACE_STORE.get(trace_id)


def find_trace_id_by_file_path(file_path: str) -> Optional[str]:
    target = os.path.abspath(file_path)

    for trace_id, trace_data in TRACE_STORE.items():
        stored_path = trace_data.get("file_path")
        if stored_path and os.path.abspath(stored_path) == target:
            return trace_id

    return None