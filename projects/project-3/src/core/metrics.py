import os
import json
from datetime import datetime

METRICS_FILE = "logs/metrics.json"

DEFAULT_METRICS = {
    "total_processed": 0,
    "approved_count": 0,
    "review_count": 0,
    "error_count": 0,
    "total_analysis_time_seconds": 0.0,
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_tokens_used": 0,
    "last_updated": None
}

def _ensure_metrics_file():
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_METRICS, f, indent=2, ensure_ascii=False)

def _merge_missing_keys(metrics: dict) -> dict:
    changed = False

    for key, value in DEFAULT_METRICS.items():
        if key not in metrics:
            metrics[key] = value
            changed = True

    if changed:
        save_metrics(metrics)

    return metrics

def load_metrics():
    _ensure_metrics_file()

    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    metrics = _merge_missing_keys(metrics)
    return metrics

def save_metrics(metrics: dict):
    metrics["last_updated"] = datetime.now().isoformat()

    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

def update_metrics(
    status: str,
    analysis_time_seconds: float,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0
):
    metrics = load_metrics()

    metrics["total_processed"] += 1
    metrics["total_analysis_time_seconds"] += analysis_time_seconds
    metrics["total_prompt_tokens"] += prompt_tokens
    metrics["total_completion_tokens"] += completion_tokens
    metrics["total_tokens_used"] += total_tokens

    if status == "approved":
        metrics["approved_count"] += 1
    elif status == "review":
        metrics["review_count"] += 1
    elif status == "error":
        metrics["error_count"] += 1

    save_metrics(metrics)

def calculate_automation_success_rate():
    metrics = load_metrics()

    total = metrics["total_processed"]
    successful = metrics["approved_count"] + metrics["review_count"]

    if total == 0:
        return 0.0

    return round((successful / total) * 100, 2)

def calculate_manual_intervention_rate():
    metrics = load_metrics()

    total = metrics["total_processed"]
    review = metrics["review_count"]

    if total == 0:
        return 0.0

    return round((review / total) * 100, 2)

def calculate_average_analysis_time():
    metrics = load_metrics()

    total = metrics["total_processed"]
    total_time = metrics["total_analysis_time_seconds"]

    if total == 0:
        return 0.0

    return round(total_time / total, 2)

def get_metrics_summary():
    metrics = load_metrics()

    return {
        **metrics,
        "automation_success_rate": calculate_automation_success_rate(),
        "manual_intervention_rate": calculate_manual_intervention_rate(),
        "average_analysis_time": calculate_average_analysis_time()
    }