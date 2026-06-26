"""Auth service.

Pure logic — no FastAPI types, no HTTP concerns. The api/auth.py router
translates between HTTP requests and these functions.
"""

from sqlmodel import Session, select

from app.core.security import hash_password, verify_password
from app.models.user import User


class EmailAlreadyRegisteredError(Exception):
    """Raised when register is called with an email that already exists."""


class InvalidCredentialsError(Exception):
    """Raised when login fails (email not found OR password wrong).

    Both cases use the same error so callers can't enumerate accounts.
    """


def register_user(
    session: Session,
    *,
    email: str,
    password: str,
    display_name: str,
) -> User:
    email = email.lower().strip()
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise EmailAlreadyRegisteredError(email)

    user = User(
        email=email,
        password_hash=hash_password(password),
        display_name=display_name.strip(),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(
    session: Session,
    *,
    email: str,
    password: str,
) -> User:
    email = email.lower().strip()
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    return user


def get_user_by_id(session: Session, user_id) -> User | None:  # noqa: ANN001
    return session.get(User, user_id)
