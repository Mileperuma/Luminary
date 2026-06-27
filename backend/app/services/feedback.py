"""Feedback service — records reactions and nudges preference weights.

Per Doc 2 §7.3 (Feedback loop):
    Love it   -> +0.10 to matched preference weights (capped at +1.0)
    Dislike   -> -0.15 to matched preference weights (capped at -1.0)
    Save      -> no weight change
    Skip      -> no weight change (logged for the same session only)
"""

from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.models.preference import MediaType, Preference, PreferenceSource
from app.models.recommendation import (
    Feedback,
    FeedbackKind,
    Recommendation,
)


class RecommendationNotFoundError(Exception):
    pass


_LOVE_DELTA = 0.10
_DISLIKE_DELTA = -0.15


def _adjust_matching_preferences(
    session: Session,
    *,
    user_id: UUID,
    media_type: MediaType,
    haystack: str,
    delta: float,
) -> int:
    """Bump every preference whose `value` text appears in the haystack."""
    rows = list(session.exec(
        select(Preference)
        .where(Preference.user_id == user_id)
        .where(Preference.media_type == media_type)
    ))
    changed = 0
    haystack = haystack.lower()
    for p in rows:
        if not p.value:
            continue
        if p.value.lower() in haystack:
            p.weight = max(-1.0, min(1.0, p.weight + delta))
            p.source = PreferenceSource.IMPLICIT
            session.add(p)
            changed += 1
    if changed:
        session.commit()
    return changed


def record_feedback(
    session: Session,
    *,
    user_id: UUID,
    recommendation_id: UUID,
    kind: FeedbackKind,
) -> tuple[Feedback, int]:
    rec = session.get(Recommendation, recommendation_id)
    if rec is None or rec.user_id != user_id:
        raise RecommendationNotFoundError()

    fb = Feedback(user_id=user_id, recommendation_id=recommendation_id, kind=kind)
    session.add(fb)
    session.commit()
    session.refresh(fb)

    delta = 0
    if kind == FeedbackKind.LOVE:
        delta = _adjust_matching_preferences(
            session,
            user_id=user_id,
            media_type=rec.media_type,
            haystack=f"{rec.title} {rec.description}",
            delta=_LOVE_DELTA,
        )
    elif kind == FeedbackKind.DISLIKE:
        delta = _adjust_matching_preferences(
            session,
            user_id=user_id,
            media_type=rec.media_type,
            haystack=f"{rec.title} {rec.description}",
            delta=_DISLIKE_DELTA,
        )

    return fb, delta
