"""Cross-media linking — given an item the user just engaged with, surface
one related item per OTHER media type.

This is the "you loved Gone Girl (book); here's the film and a long-read
about the case that inspired it" feature — the thing Goodreads/Letterboxd/
Pocket don't do.

Implementation v1 is intentionally simple: take the title + description of
the seed item, ask the LLM to name 1-2 keywords, and search each other
catalogue using those. Phase 2 sprint 7 replaces this with pgvector
similarity once embeddings exist.
"""

from __future__ import annotations

import logging
import re

from app.models.preference import MediaType
from app.models.recommendation import Recommendation
from app.services import catalogue as _catalogue
from app.services import llm_client as _llm_module
from app.services.catalogue import CatalogueClient, CatalogueItem
from app.services.llm_client import LLMClient

log = logging.getLogger("luminary.cross_media")

_OTHER_MEDIA = {
    MediaType.BOOK: [MediaType.MOVIE, MediaType.ARTICLE],
    MediaType.MOVIE: [MediaType.BOOK, MediaType.ARTICLE],
    MediaType.ARTICLE: [MediaType.BOOK, MediaType.MOVIE],
}


def _query_keywords_from_llm(seed: Recommendation, llm: LLMClient) -> str:
    """Ask the LLM for a short search-friendly query derived from the seed."""
    system = (
        "Given an item the user loved, return 3-6 plain search keywords that "
        "would help find closely related items in other media (book / film / "
        "article). Reply with just the keywords, separated by spaces. No "
        "punctuation, no labels, no quotation marks."
    )
    user_msg = (
        f"Seed item ({seed.media_type.value}):\n"
        f"Title: {seed.title}\n"
        f"Description: {seed.description[:400]}"
    )
    raw = llm.chat(system, [{"role": "user", "content": user_msg}])
    # Defensive clean — collapse to plain words.
    cleaned = re.sub(r"[^A-Za-z0-9 \-]", " ", raw)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Cap to first 10 words to keep the search URL bounded.
    return " ".join(cleaned.split()[:10])


def _client_for(media_type: MediaType) -> CatalogueClient:
    return {
        MediaType.BOOK: _catalogue.books_client,
        MediaType.MOVIE: _catalogue.movies_client,
        MediaType.ARTICLE: _catalogue.articles_client,
    }[media_type]


def find_related(
    seed: Recommendation,
    *,
    llm: LLMClient | None = None,
    fallback_query: str | None = None,
) -> dict[str, CatalogueItem]:
    """Return one related item per OTHER media type.

    Returns a dict keyed by media_type.value, e.g.
    `{"movie": CatalogueItem(...), "article": CatalogueItem(...)}`.
    Media types with no result simply don't appear in the dict.
    """
    llm = llm or _llm_module.llm_client

    query = fallback_query
    try:
        query = _query_keywords_from_llm(seed, llm) or query
    except Exception as exc:  # noqa: BLE001
        log.warning("LLM keyword extraction failed: %s", exc)
    if not query:
        # Last-resort fallback: just use the title.
        query = seed.title

    related: dict[str, CatalogueItem] = {}
    for other in _OTHER_MEDIA[seed.media_type]:
        client = _client_for(other)
        try:
            items = client.search(query=query, limit=1)
        except Exception as exc:  # noqa: BLE001
            log.warning("cross-media catalogue search (%s) failed: %s", other.value, exc)
            continue
        if items:
            related[other.value] = items[0]
    return related
