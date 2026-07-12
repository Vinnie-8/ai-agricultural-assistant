from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: UserCreate, password_hash: str) -> User:
        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=password_hash,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_by_id(self, user_id: UUID) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_all(self) -> list[User]:
        return self.db.query(User).all()

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()