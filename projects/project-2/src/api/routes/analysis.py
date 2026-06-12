from fastapi import APIRouter, HTTPException
from src.api.schemas.analysis import AnalysisRequest, AnalysisResponse
from src.services.compliance_service import analyze_text

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_recommendation(request: AnalysisRequest):
    try:
        result = analyze_text(
            text=request.text_to_analyze,
            client_profile=request.client_profile
        )
        return result

    except Exception as e:
        print("ERRO REAL:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )