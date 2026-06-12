from fastapi import FastAPI
from src.api.routes.analysis import router as analysis_router
from src.api.routes.agent_control import router as agent_control_router
from src.api.routes.metrics import router as metrics_router

app = FastAPI(
    title="Compliance Agent Platform",
    description="API para análise de conformidade e automação do agente",
    version="1.0.0"
)

app.include_router(analysis_router)
app.include_router(agent_control_router)
app.include_router(metrics_router)