from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The farmer's message.")
    location: str | None = Field(default=None)
    session_id: str = Field(
        ...,
        description=(
            "Stable conversation identifier (e.g. a chat_history session "
            "id from the backend), used to maintain conversation memory."
        ),
    )
    diagnosis_context: str | None = Field(
        default=None,
        description=(
            "Optional short description of the current diagnosis, e.g. "
            "'Crop: Maize, Disease: Common Rust, Confidence: 0.97'."
        ),
    )


class ChatResponse(BaseModel):
    reply: str
    session_id: str
