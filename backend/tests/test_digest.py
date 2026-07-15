"""Tests for the weekly digest builder + sender + opt-in endpoints."""

from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from app.core.security import hash_password
from app.models.preference import MediaType
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.digest import RecordingSender, send_weekly_digest


def _user(session: Session, *, opt_in: bool = True) -> User:
    user = User(
        email="alice@example.com",
        password_hash=hash_password("pw-1234567"),
        display_name="Alice",
        digest_opt_in=opt_in,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_recent_picks(session: Session, user: User, n: int = 2) -> None:
    for i in range(n):
        session.add(Recommendation(
            user_id=user.id, media_type=MediaType.MOVIE,
            external_id=f"tmdb:{i}", title=f"Pick {i}",
            description="a lovely pick",
            created_at=datetime.now(UTC) - timedelta(days=1),
        ))
    session.commit()


def test_send_weekly_digest_emails_opted_in_users(session: Session, monkeypatch) -> None:
    monkeypatch.setattr("app.services.digest.settings.DIGEST_ENABLED", True)
    user = _user(session)
    _seed_recent_picks(session, user)

    sender = RecordingSender()
    count = send_weekly_digest(session, sender=sender)

    assert count == 1
    assert len(sender.sent) == 1
    email = sender.sent[0]
    assert email["to"] == "alice@example.com"
    assert "your luminary picks this week" in email["subject"].lower()
    assert "Pick 0" in email["text"]
    assert "Pick 1" in email["text"]

    session.refresh(user)
    assert user.last_digest_sent_at is not None


def test_send_digest_skips_opted_out_users(session: Session, monkeypatch) -> None:
    monkeypatch.setattr("app.services.digest.settings.DIGEST_ENABLED", True)
    _user(session, opt_in=False)

    sender = RecordingSender()
    count = send_weekly_digest(session, sender=sender)

    assert count == 0
    assert sender.sent == []


def test_send_digest_skips_when_disabled_flag_is_false(session: Session, monkeypatch) -> None:
    monkeypatch.setattr("app.services.digest.settings.DIGEST_ENABLED", False)
    _user(session)

    sender = RecordingSender()
    count = send_weekly_digest(session, sender=sender)
    assert count == 0


def test_send_digest_still_sends_when_user_has_no_new_picks(session: Session, monkeypatch) -> None:
    monkeypatch.setattr("app.services.digest.settings.DIGEST_ENABLED", True)
    _user(session)

    sender = RecordingSender()
    count = send_weekly_digest(session, sender=sender)

    assert count == 1
    assert "no new picks this week" in sender.sent[0]["text"].lower()


# ---------- endpoints ----------

def test_opt_in_and_opt_out(logged_in_client) -> None:
    client, headers = logged_in_client

    res = client.post("/api/digest/opt-in", headers=headers)
    assert res.status_code == 200
    assert res.json()["digest_opt_in"] is True

    me = client.get("/api/auth/me", headers=headers).json()
    assert me["digest_opt_in"] is True

    res = client.post("/api/digest/opt-out", headers=headers)
    assert res.status_code == 200
    assert res.json()["digest_opt_in"] is False

    me = client.get("/api/auth/me", headers=headers).json()
    assert me["digest_opt_in"] is False
