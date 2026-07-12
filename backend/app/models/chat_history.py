from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.diagnosis import Diagnosis
    from app.models.user import User


class ChatHistory(BaseModel):
    __tablename__ = "chat_history"

    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    diagnosis_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("diagnoses.id"),
        nullable=True,
    )

    # Groups messages into one conversation thread. Passed to the AI
    # service as the LangGraph checkpointer's thread_id, so the agent
    # remembers prior turns within this session.
    session_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)
    reply: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_history")
    diagnosis: Mapped["Diagnosis"] = relationship(back_populates="chat_history")