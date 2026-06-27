"""Tests for /api/feedback and the preference-adjustment logic."""

from uuid import UUID

from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.preference import MediaType, Preference, PreferenceSource
from app.models.recommendation import Feedback, FeedbackKind, Recommendation
from app.models.user import User


def _seed_user_with_rec_and_pref(session: Session, *, value: str = "psychological thriller") -> tuple[User, Recommendation]:
    user = User(email="alice@example.com", password_hash=hash_password("pw-1234567"), display_name="Alice")
    session.add(user)
    session.commit()
    session.refresh(user)

    session.add(Preference(
        user_id=user.id, media_type=MediaType.MOVIE,
        key="genre", value=value, weight=0.5,
        source=PreferenceSource.CHAT,
    ))
    rec = Recommendation(
        user_id=user.id,
        media_type=MediaType.MOVIE,
        external_id="tmdb:1",
        title="Prisoners",
        description=f"A slow-burn {value} about a kidnapping.",
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return user, rec


def test_love_feedback_increases_matching_pref_weight(session: Session) -> None:
    from app.services.feedback import record_feedback
    user, rec = _seed_user_with_rec_and_pref(session)

    fb, delta = record_feedback(
        session, user_id=user.id, recommendation_id=rec.id, kind=FeedbackKind.LOVE,
    )
    assert fb.id is not None
    assert delta == 1

    pref = session.exec(select(Preference).where(Preference.user_id == user.id)).first()
    assert pref is not None
    assert pref.weight > 0.5
    assert pref.source == PreferenceSource.IMPLICIT


def test_dislike_feedback_decreases_matching_pref_weight(session: Session) -> None:
    from app.services.feedback import record_feedback
    user, rec = _seed_user_with_rec_and_pref(session)

    _, delta = record_feedback(
        session, user_id=user.id, recommendation_id=rec.id, kind=FeedbackKind.DISLIKE,
    )
    assert delta == 1

    pref = session.exec(select(Preference).where(Preference.user_id == user.id)).first()
    assert pref is not None
    assert pref.weight < 0.5


def test_save_feedback_does_not_change_weights(session: Session) -> None:
    from app.services.feedback import record_feedback
    user, rec = _seed_user_with_rec_and_pref(session)

    fb, delta = record_feedback(
        session, user_id=user.id, recommendation_id=rec.id, kind=FeedbackKind.SAVE,
    )
    assert delta == 0
    pref = session.exec(select(Preference).where(Preference.user_id == user.id)).first()
    assert pref is not None
    assert pref.weight == 0.5


def test_feedback_for_unknown_recommendation_raises(session: Session) -> None:
    import uuid

    from app.services.feedback import RecommendationNotFoundError, record_feedback
    user, _ = _seed_user_with_rec_and_pref(session)
    try:
        record_feedback(
            session, user_id=user.id, recommendation_id=uuid.uuid4(), kind=FeedbackKind.LOVE,
        )
    except RecommendationNotFoundError:
        pass
    else:
        raise AssertionError("expected RecommendationNotFoundError")


# ---------- endpoint ----------

def test_post_feedback_endpoint_records_row(logged_in_client) -> None:
    client, headers = logged_in_client

    # Seed a recommendation directly via the DB session override —
    # the conftest's logged_in_client already created the user.
    from app.api.deps import get_session
    from app.main import app
    session = next(app.dependency_overrides[get_session]())

    me = client.get("/api/auth/me", headers=headers).json()
    rec = Recommendation(
        user_id=UUID(me["id"]), media_type=MediaType.MOVIE,
        external_id="tmdb:99", title="X", description="psychological thriller",
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)

    res = client.post(
        "/api/feedback",
        headers=headers,
        json={"recommendation_id": str(rec.id), "kind": "love"},
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["kind"] == "love"
    assert body["recommendation_id"] == str(rec.id)

    rows = list(session.exec(select(Feedback).where(Feedback.recommendation_id == rec.id)))
    assert len(rows) == 1


def test_post_feedback_to_unknown_recommendation_returns_404(logged_in_client) -> None:
    client, headers = logged_in_client
    res = client.post(
        "/api/feedback",
        headers=headers,
        json={
            "recommendation_id": "00000000-0000-0000-0000-000000000000",
            "kind": "love",
        },
    )
    assert res.status_code == 404
