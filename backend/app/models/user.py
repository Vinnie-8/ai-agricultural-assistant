from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import BaseModel
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.diagnosis import Diagnosis
    from app.models.chat_history import ChatHistory


class User(BaseModel):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="farmer"
    )
    diagnoses: Mapped[list["Diagnosis"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan")
    chat_history: Mapped[list["ChatHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan")