"""Recommender service — picks a primary item + similar items per media type.

Phase 1 ranking is simple keyword scoring against the user's stored preferences.
Phase 2 replaces this with pgvector similarity (see Sprint 7).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from uuid import UUID

from sqlmodel import Session, select

from app.models.preference import MediaType, Preference
from app.models.recommendation import Recommendation
from app.services import catalogue as _catalogue
from app.services import llm_client as _llm_module
from app.services.catalogue import CatalogueClient, CatalogueItem
from app.services.llm_client import LLMClient

log = logging.getLogger("luminary.recommender")

MIN_SIMILAR = 4


@dataclass
class RecommendationResult:
    primary: CatalogueItem
    similar: list[CatalogueItem]
    explanation: str


# ---------- query building ----------

def _build_query(preferences: list[Preference], media_type: MediaType, mood: str | None) -> str:
    """Turn the user's preferences into a search query for the external API."""
    relevant = [p for p in preferences if p.media_type == media_type and p.weight > 0]
    relevant.sort(key=lambda p: p.weight, reverse=True)
    parts = [p.value for p in relevant[:3]]
    if mood:
        parts.append(mood)
    if not parts:
        # Cold start — return a sensible default per media type.
        return {
            MediaType.BOOK: "literary fiction",
            MediaType.MOVIE: "drama",
            MediaType.ARTICLE: "longform feature",
        }[media_type]
    return " ".join(parts)


# ---------- ranking ----------

def _score_candidate(item: CatalogueItem, preferences: list[Preference]) -> float:
    """Cheap text-overlap score: how many preference values appear in the
    item's title + description + keywords. Weighted by preference weight."""
    text = " ".join([item.title, item.description, *(item.keywords or [])]).lower()
    score = 0.0
    for p in preferences:
        if p.media_type != item.media_type:
            continue
        if p.value.lower() in text:
            score += p.weight
    return score


def _summarise_profile(preferences: list[Preference], media_type: MediaType) -> str:
    relevant = sorted(
        (p for p in preferences if p.media_type == media_type),
        key=lambda p: p.weight,
        reverse=True,
    )[:8]
    if not relevant:
        return "A new user who has not set preferences yet."
    lines = [f"- {p.key}: {p.value} (weight {p.weight:.1f})" for p in relevant]
    return "\n".join(lines)


# ---------- main entry ----------

def recommend(
    session: Session,
    *,
    user_id: UUID,
    media_type: MediaType,
    mood: str | None = None,
    # Injection seams for tests
    books: CatalogueClient | None = None,
    movies: CatalogueClient | None = None,
    articles: CatalogueClient | None = None,
    youtube=None,
    llm: LLMClient | None = None,
) -> Recommendation:
    """Produce one Recommendation row + return the saved entity."""
    # Resolve via the modules (not imported names) so tests can patch
    # the module-level singletons and have it actually take effect here.
    books = books or _catalogue.books_client
    movies = movies or _catalogue.movies_client
    articles = articles or _catalogue.articles_client
    youtube = youtube or _catalogue.youtube_client
    llm = llm or _llm_module.llm_client

    preferences = list(session.exec(select(Preference).where(Preference.user_id == user_id)))

    query = _build_query(preferences, media_type, mood)
    catalogue = {
        MediaType.BOOK: books,
        MediaType.MOVIE: movies,
        MediaType.ARTICLE: articles,
    }[media_type]

    candidates = catalogue.search(query=query, mood=mood, limit=12)
    if not candidates:
        raise RecommendationUnavailableError(media_type)

    ranked = sorted(
        candidates,
        key=lambda item: _score_candidate(item, preferences),
        reverse=True,
    )
    primary = ranked[0]
    similar = ranked[1 : 1 + MIN_SIMILAR]

    # Pad similars if fewer than MIN_SIMILAR came back
    while len(similar) < MIN_SIMILAR and len(ranked) > 1 + len(similar):
        similar.append(ranked[1 + len(similar)])

    # Trailer enrichment for movies
    trailer_url = None
    if media_type == MediaType.MOVIE:
        trailer_url = youtube.trailer_url(title=primary.title)

    # LLM explanation
    profile_summary = _summarise_profile(preferences, media_type)
    explanation = llm.explain_recommendation(profile_summary, primary.to_dict())

    rec = Recommendation(
        user_id=user_id,
        media_type=media_type,
        external_id=primary.external_id,
        title=primary.title,
        image_url=primary.image_url,
        trailer_url=trailer_url,
        description=explanation,
        similar_items=[s.to_dict() for s in similar],
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return rec


class RecommendationUnavailableError(Exception):
    """Raised when no candidate items came back from the catalogue."""

    def __init__(self, media_type: MediaType) -> None:
        super().__init__(f"no candidates for {media_type.value}")
        self.media_type = media_type
