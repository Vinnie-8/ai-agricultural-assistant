from uuid import UUID

from sqlalchemy.orm import Session

from app.models.chat_history import ChatHistory


class ChatRepository:
    @staticmethod
    def create(
        db: Session,
        session_id: str,
        message: str,
        reply: str,
        user_id: UUID | None = None,
        diagnosis_id: UUID | None = None,
    ) -> ChatHistory:
        chat_entry = ChatHistory(
            session_id=session_id,
            message=message,
            reply=reply,
            user_id=user_id,
            diagnosis_id=diagnosis_id,
        )
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)
        return chat_entry