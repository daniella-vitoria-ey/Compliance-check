from fastapi import APIRouter
from src.core.metrics import get_metrics_summary, load_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/summary")
def metrics_summary():
    return get_metrics_summary()

@router.get("/raw")
def metrics_raw():
    return load_metrics()