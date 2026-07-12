from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr,Field


class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=64)


class UserResponse(UserBase):
    id: UUID
    role: str

    model_config = ConfigDict(from_attributes=True)