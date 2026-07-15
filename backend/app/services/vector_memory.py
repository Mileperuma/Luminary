"""Vector memory — builds per-user taste vectors and ranks candidates against them.

Written so it's a *drop-in* upgrade for the keyword scorer in `recommender.py`:
- `rebuild_user_embedding()` regenerates the profile vector for one media type.
- `rank_by_similarity()` reorders candidate items by cosine distance to the
  profile vector. When there's no profile vector (cold start, offline mode)
  the caller keeps whatever ordering they had.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlmodel import Session, select

from app.models.preference import MediaType, Preference
from app.models.preference_embedding import PreferenceEmbedding
from app.services import embeddings as _embeddings_module
from app.services.catalogue import CatalogueItem
from app.services.embeddings import EmbeddingClient

log = logging.getLogger("luminary.vector_memory")


def _summarise_preferences(rows: list[Preference]) -> str:
    """Human-readable summary of a user's positive preferences per media type."""
    positive = [p for p in rows if p.weight > 0]
    positive.sort(key=lambda p: p.weight, reverse=True)
    lines = [f"- {p.key}: {p.value} (weight {p.weight:.2f})" for p in positive[:20]]
    return "\n".join(lines) if lines else "(no preferences yet)"


def rebuild_user_embedding(
    session: Session,
    *,
    user_id: UUID,
    media_type: MediaType,
    client: EmbeddingClient | None = None,
) -> PreferenceEmbedding:
    """Recompute and persist the profile vector for one user + media type."""
    client = client or _embeddings_module.embedding_client

    rows = list(session.exec(
        select(Preference)
        .where(Preference.user_id == user_id)
        .where(Preference.media_type == media_type)
    ))
    summary = _summarise_preferences(rows)
    vector = client.embed(summary)

    existing = session.exec(
        select(PreferenceEmbedding)
        .where(PreferenceEmbedding.user_id == user_id)
        .where(PreferenceEmbedding.media_type == media_type)
    ).first()

    if existing:
        existing.embedding = vector
        existing.summary = summary
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    new = PreferenceEmbedding(
        user_id=user_id,
        media_type=media_type,
        embedding=vector,
        summary=summary,
    )
    session.add(new)
    session.commit()
    session.refresh(new)
    return new


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def rank_by_similarity(
    session: Session,
    *,
    user_id: UUID,
    media_type: MediaType,
    candidates: list[CatalogueItem],
    client: EmbeddingClient | None = None,
) -> list[CatalogueItem]:
    """Reorder candidates by cosine similarity to the stored profile vector.

    Returns the candidates unchanged if no profile vector exists yet, if we
    can't embed any candidates, or on any provider error.
    """
    if not candidates:
        return candidates

    client = client or _embeddings_module.embedding_client

    profile = session.exec(
        select(PreferenceEmbedding)
        .where(PreferenceEmbedding.user_id == user_id)
        .where(PreferenceEmbedding.media_type == media_type)
    ).first()
    if profile is None or not profile.embedding:
        return candidates

    scored: list[tuple[float, CatalogueItem]] = []
    for item in candidates:
        text = f"{item.title}. {item.description}"
        try:
            vec = client.embed(text)
        except Exception as exc:  # noqa: BLE001
            log.warning("candidate embed failed: %s", exc)
            return candidates
        scored.append((_cosine(list(profile.embedding), vec), item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored]
