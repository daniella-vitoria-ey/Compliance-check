import os
import json

STATUS_FILE = "logs/agent_status.json"

DEFAULT_STATUS = {
    "last_file": None,
    "status": "idle",
    "destination": None,
    "reason": None,
    "result": None,
    "trace_id": None
}

def _ensure_file():
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_STATUS, f, indent=2, ensure_ascii=False)

def save_agent_status(data: dict):
    _ensure_file()
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_agent_status():
    _ensure_file()
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)