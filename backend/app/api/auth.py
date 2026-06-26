"""Auth endpoints: register, login, current user."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from app.services.auth import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
)

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: SessionDep) -> UserPublic:
    try:
        user = register_user(
            session,
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="an account with that email already exists",
        ) from exc

    return UserPublic.model_validate(user.model_dump())


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: SessionDep) -> TokenResponse:
    try:
        user = authenticate_user(session, email=payload.email, password=payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        ) from exc

    # Update last_login_at
    user.last_login_at = datetime.now(UTC)
    session.add(user)
    session.commit()

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRES_MINUTES,
    )


@router.get("/me", response_model=UserPublic)
def me(current_user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(current_user.model_dump())
