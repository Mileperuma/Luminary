"""Memory service — builds the returning-user welcome experience.

The greeting is templated, not LLM-generated, for two reasons:
- It's the first impression on every visit; deterministic latency matters.
- It can't accidentally hallucinate preferences the user didn't actually state.

A user with no stored preferences gets a softer fall-through greeting that
nudges them toward onboarding instead of pretending we know them.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.models.preference import MediaType, Preference
from app.models.recommendation import Recommendation
from app.models.user import User

LONG_ABSENCE_DAYS = 30


@dataclass
class MemorySummary:
    """What the memory layer knows about a user, used to build the greeting."""

    top_per_media: dict[MediaType, list[Preference]] = field(default_factory=dict)
    last_login_at: datetime | None = None
    long_absence: bool = False
    recent_picks: list[Recommendation] = field(default_factory=list)


@dataclass
class WelcomePayload:
    """Frontend-facing greeting + the items to render under it."""

    greeting: str
    is_returning: bool
    needs_onboarding: bool
    fresh_picks: list[dict]


# ---------- builder ----------

def build_summary(session: Session, *, user: User) -> MemorySummary:
    preferences = list(session.exec(
        select(Preference)
        .where(Preference.user_id == user.id)
        .where(Preference.weight > 0)  # only positive preferences shape the greeting
    ))

    grouped: dict[MediaType, list[Preference]] = defaultdict(list)
    for p in preferences:
        grouped[p.media_type].append(p)
    for media in grouped:
        grouped[media].sort(key=lambda p: p.weight, reverse=True)

    recent_picks = list(session.exec(
        select(Recommendation)
        .where(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc())  # type: ignore[attr-defined]
        .limit(3)
    ))

    long_absence = False
    if user.last_login_at:
        gap = datetime.now(UTC) - user.last_login_at
        long_absence = gap >= timedelta(days=LONG_ABSENCE_DAYS)

    return MemorySummary(
        top_per_media={m: rows[:3] for m, rows in grouped.items()},
        last_login_at=user.last_login_at,
        long_absence=long_absence,
        recent_picks=recent_picks,
    )


# ---------- greeting templating ----------

def _media_phrase(media: MediaType) -> str:
    return {MediaType.BOOK: "reading", MediaType.MOVIE: "watching", MediaType.ARTICLE: "long reads"}[media]


def _format_top_signals(summary: MemorySummary) -> str | None:
    """Find the single strongest signal across all media to name in the greeting."""
    pool = [(m, p) for m, rows in summary.top_per_media.items() for p in rows]
    if not pool:
        return None
    pool.sort(key=lambda mp: mp[1].weight, reverse=True)
    media, top = pool[0]
    return f"{top.value} ({_media_phrase(media)})"


def build_greeting(user: User, summary: MemorySummary) -> WelcomePayload:
    name = user.display_name.strip()
    fresh = [
        {
            "id": str(r.id),
            "media_type": r.media_type.value,
            "title": r.title,
            "image_url": r.image_url,
            "trailer_url": r.trailer_url,
            "description": r.description,
        }
        for r in summary.recent_picks
    ]

    has_prefs = any(summary.top_per_media.values())

    if not has_prefs:
        return WelcomePayload(
            greeting=(
                f"Welcome, {name}. Tell me what you like and I'll start recommending "
                "things that fit."
            ),
            is_returning=summary.last_login_at is not None,
            needs_onboarding=True,
            fresh_picks=fresh,
        )

    signal = _format_top_signals(summary)
    lead = f"Welcome back, {name}." if summary.last_login_at else f"Welcome, {name}."

    body_parts: list[str] = []
    if summary.long_absence:
        body_parts.append("It's been a while — picking up where we left off.")
    if signal:
        body_parts.append(f"You loved {signal} last time; here are fresh picks in that vein.")

    greeting = lead if not body_parts else f"{lead} " + " ".join(body_parts)

    return WelcomePayload(
        greeting=greeting,
        is_returning=summary.last_login_at is not None,
        needs_onboarding=False,
        fresh_picks=fresh,
    )


def welcome(session: Session, *, user: User) -> WelcomePayload:
    return build_greeting(user, build_summary(session, user=user))


__all__ = [
    "LONG_ABSENCE_DAYS",
    "MemorySummary",
    "WelcomePayload",
    "build_greeting",
    "build_summary",
    "welcome",
]
