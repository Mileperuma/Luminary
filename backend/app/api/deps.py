"""Shared FastAPI dependencies.

Importing `get_current_user` into a route gives you the authenticated
`User` row directly — or a 401 if the token is missing/invalid.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import InvalidTokenError, decode_access_token
from app.models.user import User
from app.services.auth import get_user_by_id

SessionDep = Annotated[Session, Depends(get_session)]


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ", 1)[1].strip()


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: SessionDep = None,  # type: ignore[assignment]
) -> User:
    token = _extract_token(authorization)
    try:
        user_id = decode_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
