from pydantic import BaseModel, Field
from typing import List


class AnalysisRequest(BaseModel):
    text_to_analyze: str = Field(
        ...,
        min_length=10,
        description="Texto da recomendação a ser analisada."
    )
    client_profile: str = Field(
        ...,
        description="Perfil do cliente. Ex.: conservador, moderado ou arrojado."
    )

class Source(BaseModel):
    source_document: str
    source_chunk_id: str

class Usage(BaseModel):
    prompt_tokens: int = Field(
        default=0,
        description="Quantidade de tokens usados no prompt."
    )
    completion_tokens: int = Field(
        default=0,
        description="Quantidade de tokens usados na resposta."
    )
    total_tokens: int = Field(
        default=0,
        description="Quantidade total de tokens usados na chamada."
    )

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
    sources: List[Source] = Field(
        default_factory=list,
        description="Fontes utilizadas na análise."
    )
    usage: Usage = Field(
        default_factory=Usage,
        description="Informações de uso de tokens da chamada ao modelo."
    )