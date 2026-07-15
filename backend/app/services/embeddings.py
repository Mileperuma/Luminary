"""Embeddings adapter — wraps whichever provider is configured.

Same pattern as llm_client.py: an offline mode that returns a deterministic
zero vector so tests and cold-start dev environments still work when no API
key is present. The offline vector has no similarity meaning, but downstream
code just treats it as "nothing to compare against" and falls back to the
keyword ranking that already exists in the recommender.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Protocol

import openai

from app.core.config import get_settings
from app.models.preference_embedding import EMBEDDING_DIM

log = logging.getLogger("luminary.embeddings")
settings = get_settings()


class EmbeddingClient(Protocol):
    def embed(self, text: str) -> list[float]: ...


class _OpenAIEmbeddings:
    def __init__(self, api_key: str) -> None:
        self._client = openai.OpenAI(api_key=api_key)

    def embed(self, text: str) -> list[float]:
        resp = self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
        )
        vec = resp.data[0].embedding
        return list(vec)


class _OfflineEmbeddings:
    """Deterministic offline stand-in — a hash-derived pseudo-vector.

    Different inputs give different vectors, so pgvector distance is still
    monotonic-ish, but they carry no semantic signal. Good enough for tests
    and demo mode; not usable for real recall.
    """

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        raw = list(digest * ((EMBEDDING_DIM * 4 // len(digest)) + 1))[: EMBEDDING_DIM * 4]
        vec: list[float] = []
        for i in range(0, len(raw), 4):
            # normalise each 4-byte int into [-1, 1]
            n = int.from_bytes(raw[i:i + 4], "big", signed=True)
            vec.append(n / 2_147_483_647)
        return vec[:EMBEDDING_DIM]


class _Adapter:
    def __init__(self) -> None:
        self._primary: EmbeddingClient | None = None
        if settings.OPENAI_API_KEY:
            self._primary = _OpenAIEmbeddings(settings.OPENAI_API_KEY)
        self._offline = _OfflineEmbeddings()

    def embed(self, text: str) -> list[float]:
        if self._primary is None:
            return self._offline.embed(text)
        try:
            return self._primary.embed(text)
        except Exception as exc:  # noqa: BLE001
            log.warning("embedding call failed, using offline fallback: %s", exc)
            return self._offline.embed(text)


embedding_client: EmbeddingClient = _Adapter()


class FakeEmbeddingClient:
    """Test helper — returns a fixed vector, records every call."""

    def __init__(self, vector: list[float] | None = None) -> None:
        self._vector = vector or ([0.1] * EMBEDDING_DIM)
        self.calls: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return list(self._vector)
