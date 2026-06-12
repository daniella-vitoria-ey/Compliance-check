from pydantic import BaseModel, Field
from typing import List

#Define um modelo de entrada da API
class AnalysisRequest(BaseModel):
    text_to_analyze: str = Field(
        ...,
        min_length=10,
        description="Texto da recomendação a ser analisada."
    )

#Define um modelo de saída da API
class AnalysisResponse(BaseModel):
    is_compliant: bool = Field(
        ...,
        description="Indica se a recomendação está em conformidade."
    )
    reason: str = Field(
        ...,
        description="Justificativa detalhada da análise."
    )
    mentioned_products: List[str] = Field(
        default_factory=list,
        description="Lista de produtos mencionados."
    )