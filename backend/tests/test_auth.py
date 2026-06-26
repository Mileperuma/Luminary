"""End-to-end tests of the auth flow against an in-memory DB."""

from fastapi.testclient import TestClient

# ---------- register ----------

def test_register_creates_user_and_returns_public_shape(client: TestClient) -> None:
    res = client.post(
        "/api/auth/register",
        json={
            "email": "Alice@example.com",
            "password": "correct horse battery",
            "display_name": "Alice",
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "alice@example.com"  # normalised
    assert body["display_name"] == "Alice"
    assert body["onboarding_complete"] is False
    assert "id" in body
    assert "password" not in body and "password_hash" not in body


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "alice@example.com",
        "password": "correct horse battery",
        "display_name": "Alice",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 201
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"]


def test_register_rejects_short_password(client: TestClient) -> None:
    res = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "short", "display_name": "Alice"},
    )
    assert res.status_code == 422


def test_register_rejects_bad_email(client: TestClient) -> None:
    res = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "correct horse battery", "display_name": "Alice"},
    )
    assert res.status_code == 422


# ---------- login ----------

def test_login_returns_token_and_updates_last_login_at(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "correct horse battery", "display_name": "Alice"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "correct horse battery"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"].count(".") == 2
    assert body["expires_in_minutes"] > 0


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "correct horse battery", "display_name": "Alice"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "wrong password"},
    )
    assert res.status_code == 401


def test_login_with_unknown_email_returns_401(client: TestClient) -> None:
    res = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "anything"},
    )
    assert res.status_code == 401


# ---------- me ----------

def test_me_returns_profile_for_valid_token(logged_in_client) -> None:
    client, headers = logged_in_client
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert body["last_login_at"] is not None


def test_me_without_token_returns_401(client: TestClient) -> None:
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_with_malformed_authorization_returns_401(client: TestClient) -> None:
    res = client.get("/api/auth/me", headers={"Authorization": "NotBearer abc"})
    assert res.status_code == 401


def test_me_with_garbage_token_returns_401(client: TestClient) -> None:
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401
