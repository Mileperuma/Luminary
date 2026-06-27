"""Tests for the memory service and GET /api/memory/welcome."""

from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from app.core.security import hash_password
from app.models.preference import MediaType, Preference, PreferenceSource
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.memory import LONG_ABSENCE_DAYS, build_summary, welcome


def _user(session: Session, *, last_login_at: datetime | None = None) -> User:
    user = User(
        email="alice@example.com",
        password_hash=hash_password("pw-1234567"),
        display_name="Alice",
        last_login_at=last_login_at,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ---------- service ----------

def test_summary_groups_preferences_by_media(session: Session) -> None:
    user = _user(session)
    session.add(Preference(user_id=user.id, media_type=MediaType.MOVIE,
                           key="genre", value="thriller", weight=0.9,
                           source=PreferenceSource.CHAT))
    session.add(Preference(user_id=user.id, media_type=MediaType.BOOK,
                           key="genre", value="literary fiction", weight=0.8,
                           source=PreferenceSource.CHAT))
    session.add(Preference(user_id=user.id, media_type=MediaType.BOOK,
                           key="tone", value="hopeful", weight=-0.4,   # negative
                           source=PreferenceSource.CHAT))
    session.commit()

    summary = build_summary(session, user=user)
    assert set(summary.top_per_media.keys()) == {MediaType.MOVIE, MediaType.BOOK}
    # Negative-weight prefs excluded
    assert all(p.weight > 0 for prefs in summary.top_per_media.values() for p in prefs)


def test_welcome_for_new_user_with_no_prefs_nudges_to_onboarding(session: Session) -> None:
    user = _user(session)
    payload = welcome(session, user=user)
    assert payload.needs_onboarding is True
    assert payload.is_returning is False
    assert "tell me what you like" in payload.greeting.lower()


def test_welcome_for_returning_user_with_prefs_names_a_specific_taste(session: Session) -> None:
    user = _user(session, last_login_at=datetime.now(UTC) - timedelta(days=2))
    session.add(Preference(user_id=user.id, media_type=MediaType.MOVIE,
                           key="genre", value="psychological thriller", weight=0.95,
                           source=PreferenceSource.CHAT))
    session.add(Preference(user_id=user.id, media_type=MediaType.BOOK,
                           key="genre", value="literary fiction", weight=0.7,
                           source=PreferenceSource.CHAT))
    session.commit()

    payload = welcome(session, user=user)
    assert payload.needs_onboarding is False
    assert payload.is_returning is True
    assert "welcome back" in payload.greeting.lower()
    # Names the strongest signal
    assert "psychological thriller" in payload.greeting.lower()


def test_welcome_after_long_absence_acknowledges_gap(session: Session) -> None:
    user = _user(
        session,
        last_login_at=datetime.now(UTC) - timedelta(days=LONG_ABSENCE_DAYS + 1),
    )
    session.add(Preference(user_id=user.id, media_type=MediaType.MOVIE,
                           key="genre", value="thriller", weight=0.9,
                           source=PreferenceSource.CHAT))
    session.commit()
    payload = welcome(session, user=user)
    assert "been a while" in payload.greeting.lower()


def test_welcome_includes_recent_picks(session: Session) -> None:
    user = _user(session, last_login_at=datetime.now(UTC) - timedelta(days=1))
    session.add(Preference(user_id=user.id, media_type=MediaType.MOVIE,
                           key="genre", value="drama", weight=0.8,
                           source=PreferenceSource.CHAT))
    session.add(Recommendation(
        user_id=user.id, media_type=MediaType.MOVIE,
        external_id="tmdb:1", title="A Slow Burn", description="why",
    ))
    session.commit()

    payload = welcome(session, user=user)
    assert len(payload.fresh_picks) == 1
    assert payload.fresh_picks[0]["title"] == "A Slow Burn"


# ---------- endpoint ----------

def test_get_welcome_endpoint(logged_in_client) -> None:
    client, headers = logged_in_client
    res = client.get("/api/memory/welcome", headers=headers)
    assert res.status_code == 200
    body = res.json()
    # Brand-new logged_in_client has no prefs, so onboarding nudge is expected
    assert body["needs_onboarding"] is True
    assert body["is_returning"] is True  # they just logged in once already
    assert "alice" in body["greeting"].lower()
    assert body["fresh_picks"] == []


def test_welcome_endpoint_requires_auth(client) -> None:
    res = client.get("/api/memory/welcome")
    assert res.status_code == 401
