from pydantic import BaseModel, Field
from typing import List


class SupportRequest(BaseModel):
    query: str


class SupportResponse(BaseModel):
    answer: str

    sources: List[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )