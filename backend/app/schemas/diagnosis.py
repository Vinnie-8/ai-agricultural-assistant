from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DiagnosisResponse(BaseModel):
    id: UUID
    crop: str
    disease: str
    confidence: float
    recommendation: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)