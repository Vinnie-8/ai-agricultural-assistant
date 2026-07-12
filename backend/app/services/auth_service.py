from uuid import UUID

from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.utils.security import (
    hash_password,
    verify_password,
)


class AuthService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, user_data: UserCreate) -> UserResponse:

        existing_user = self.repository.get_by_email(user_data.email)

        if existing_user:
            raise ValueError("Email already registered")

        password_hash = hash_password(user_data.password)

        user = self.repository.create(
            user_data=user_data,
            password_hash=password_hash,
        )

        return UserResponse.model_validate(user)

    def login(self, credentials: LoginRequest) -> Token:

        user = self.repository.get_by_email(credentials.email)

        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(
            credentials.password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        