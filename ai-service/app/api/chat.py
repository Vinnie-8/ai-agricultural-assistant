from fastapi import APIRouter, HTTPException, status

from app.agents.farming_agent import run_chat
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(request: ChatRequest):
    try:
        reply = run_chat(
            message=request.message,
            session_id=request.session_id,
            diagnosis_context=request.diagnosis_context,
            location=request.location,
        )
    except Exception as e:
        # Broad catch is intentional here: this is a boundary against the
        # LLM/agent stack (network errors, API errors, tool failures), and
        # we want a clean 500 rather than leaking a stack trace to the
        # caller. Replace with narrower exception handling as failure
        # modes become clearer during testing.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat agent error: {e}",
        )

    return ChatResponse(reply=reply, session_id=request.session_id)
