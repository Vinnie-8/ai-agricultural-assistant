from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.diagnosis_repository import DiagnosisRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_client import AIClient, AIServiceError

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diagnosis_context = None

    if request.diagnosis_id:
        diagnosis = DiagnosisRepository.get_by_id(db, request.diagnosis_id)
        if diagnosis:
            diagnosis_context = (
                f"Crop: {diagnosis.crop}, Disease: {diagnosis.disease}, "
                f"Confidence: {diagnosis.confidence}"
            )

    try:
        reply = AIClient.chat(
            message=request.message,
            session_id=request.session_id,
            diagnosis_context=diagnosis_context,
            location=request.location,
        )
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )

    chat_entry = ChatRepository.create(
        db=db,
        session_id=request.session_id,
        message=request.message,
        reply=reply,
        user_id=current_user.id,
        diagnosis_id=request.diagnosis_id,
    )

    return chat_entry