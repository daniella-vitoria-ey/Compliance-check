from fastapi import APIRouter, HTTPException
from src.api.schemas.analysis import AnalysisRequest, AnalysisResponse
from src.services.compliance_service import analyze_text
from src.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_recommendation(request: AnalysisRequest):
    try:
        result = analyze_text(
            text=request.text_to_analyze,
            client_profile=request.client_profile
        )
        return result

    except Exception as e:
        logger.exception(f"Erro real na rota /analyze: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )