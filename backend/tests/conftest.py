"""Shared pytest fixtures.

Uses an in-memory SQLite database for fast, isolated unit tests. Real PG
integration tests live in /backend/tests/integration/* (added later) and run
against the Postgres service defined in .github/workflows/ci.yml.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_current_user
from app.core.db import get_session
from app.main import app
from app.models import User  # noqa: F401  -- ensure models are registered


@pytest.fixture(name="session")
def session_fixture() -> Iterator[Session]:
    """Fresh in-memory SQLite per test — total isolation, microsecond setup.

    pgvector-only features (vector similarity) are excluded from this fixture
    by design; tests that need them belong in tests/integration/.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Iterator[TestClient]:
    """Test client with the DB session dependency overridden to the in-memory engine."""

    def _override_session() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_session] = _override_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="logged_in_client")
def logged_in_client_fixture(client: TestClient) -> tuple[TestClient, dict]:
    """Register + log in a user and return (client, headers_with_token)."""
    payload = {
        "email": "alice@example.com",
        "password": "correct horse battery",
        "display_name": "Alice",
    }
    client.post("/api/auth/register", json=payload)
    login = client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    token = login.json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.pop(get_current_user, None)
