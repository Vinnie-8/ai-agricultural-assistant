from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field(
        ...,
        description="Stable conversation identifier from the frontend/client.",
    )
    diagnosis_id: UUID | None = Field(
        default=None,
        description="Optional diagnosis this chat is grounded in.",
    )
    location: str | None = Field(default=None)


class ChatResponse(BaseModel):
    id: UUID
    session_id: str
    message: str
    reply: str

    class Config:
        from_attributes = True