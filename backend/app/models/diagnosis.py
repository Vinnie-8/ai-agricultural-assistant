from sqlalchemy import String, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.chat_history import ChatHistory
import uuid
from app.models.base_model import BaseModel


class Diagnosis(BaseModel):
    __tablename__ = "diagnoses"

    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    image_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    crop: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    disease: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="completed",
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="diagnoses"
    )
    chat_history: Mapped[list["ChatHistory"]] = relationship(
        back_populates="diagnosis",
        cascade="all, delete-orphan",
    )