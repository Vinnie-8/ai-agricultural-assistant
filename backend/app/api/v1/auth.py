from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_auth_service
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.utils.jwt import decode_token, create_tokens

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.register(user)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
)
def login(
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.login(credentials)

    except ValueError as e:from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_auth_service
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.utils.jwt import decode_token, create_tokens

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.register(user)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
)
def login(
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.login(credentials)

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=Token,
)
def refresh(
    refresh_token: str,
):
    payload = decode_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    user_id = payload["sub"]

    return create_tokens(user_id)
    raise HTTPException(
            status_code=401,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=Token,
)
def refresh(
    refresh_token: str,
):
    payload = decode_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    user_id = payload["sub"]

    return create_tokens(user_id)