"""External content catalogue adapters — Books, Movies, Articles, YouTube.

Each adapter returns a uniform `CatalogueItem` so the recommender doesn't
have to know which source produced it. Adapters are sync httpx for simplicity;
each call to FastAPI is already running in its own thread.
"""

from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass, field
from typing import Protocol

import httpx

from app.core.config import get_settings
from app.models.preference import MediaType

log = logging.getLogger("luminary.catalogue")
settings = get_settings()


# ---------- uniform item shape ----------

@dataclass
class CatalogueItem:
    media_type: MediaType
    external_id: str       # "gbooks:abc", "tmdb:603", "guardian:slug"
    title: str
    description: str
    image_url: str | None = None
    trailer_url: str | None = None
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self) | {"media_type": self.media_type.value}


class CatalogueClient(Protocol):
    def search(self, *, query: str, mood: str | None = None, limit: int = 8) -> list[CatalogueItem]: ...


# ---------- BOOKS — Google Books API ----------

class BooksClient:
    """Google Books — free, no approval gate, covers ISBN + cover + description."""

    BASE = "https://www.googleapis.com/books/v1"

    def search(self, *, query: str, mood: str | None = None, limit: int = 8) -> list[CatalogueItem]:
        params = {"q": query, "maxResults": limit, "printType": "books"}
        if settings.GOOGLE_BOOKS_API_KEY:
            params["key"] = settings.GOOGLE_BOOKS_API_KEY
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{self.BASE}/volumes", params=params)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("Google Books fetch failed: %s", exc)
            return []

        items: list[CatalogueItem] = []
        for vol in data.get("items", [])[:limit]:
            info = vol.get("volumeInfo", {})
            title = info.get("title")
            if not title:
                continue
            authors = ", ".join(info.get("authors", []))
            description = info.get("description") or info.get("subtitle") or ""
            image = (info.get("imageLinks") or {}).get("thumbnail")
            items.append(CatalogueItem(
                media_type=MediaType.BOOK,
                external_id=f"gbooks:{vol.get('id')}",
                title=f"{title}" + (f" — {authors}" if authors else ""),
                description=description,
                image_url=image,
                keywords=info.get("categories", []) or [],
            ))
        return items


# ---------- MOVIES — TMDb ----------

class MoviesClient:
    """TMDb — free metadata + poster URLs + trailer keys."""

    BASE = "https://api.themoviedb.org/3"
    POSTER_BASE = "https://image.tmdb.org/t/p/w500"

    def search(self, *, query: str, mood: str | None = None, limit: int = 8) -> list[CatalogueItem]:
        if not settings.TMDB_API_KEY:
            log.info("TMDB_API_KEY not configured; movies adapter returning empty list")
            return []
        params = {"api_key": settings.TMDB_API_KEY, "query": query, "include_adult": "false"}
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{self.BASE}/search/movie", params=params)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("TMDb fetch failed: %s", exc)
            return []

        items: list[CatalogueItem] = []
        for movie in data.get("results", [])[:limit]:
            title = movie.get("title")
            if not title:
                continue
            poster = movie.get("poster_path")
            items.append(CatalogueItem(
                media_type=MediaType.MOVIE,
                external_id=f"tmdb:{movie.get('id')}",
                title=title,
                description=movie.get("overview") or "",
                image_url=f"{self.POSTER_BASE}{poster}" if poster else None,
                # trailer URL is fetched lazily by the YouTube adapter
                keywords=[],
            ))
        return items


# ---------- ARTICLES — Guardian Open Platform ----------

class ArticlesClient:
    """The Guardian Open Platform — free, high-quality long-form with images."""

    BASE = "https://content.guardianapis.com/search"

    def search(self, *, query: str, mood: str | None = None, limit: int = 8) -> list[CatalogueItem]:
        if not settings.GUARDIAN_API_KEY:
            log.info("GUARDIAN_API_KEY not configured; articles adapter returning empty list")
            return []
        params = {
            "api-key": settings.GUARDIAN_API_KEY,
            "q": query,
            "show-fields": "trailText,thumbnail",
            "page-size": limit,
            "order-by": "relevance",
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(self.BASE, params=params)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("Guardian fetch failed: %s", exc)
            return []

        items: list[CatalogueItem] = []
        for art in data.get("response", {}).get("results", [])[:limit]:
            fields = art.get("fields", {})
            items.append(CatalogueItem(
                media_type=MediaType.ARTICLE,
                external_id=f"guardian:{art.get('id')}",
                title=art.get("webTitle", ""),
                description=fields.get("trailText", "") or "",
                image_url=fields.get("thumbnail"),
                keywords=[art.get("sectionName")] if art.get("sectionName") else [],
            ))
        return items


# ---------- TRAILERS — YouTube Data API ----------

class YouTubeClient:
    """Looks up the top trailer for a movie title using YouTube Data API."""

    BASE = "https://www.googleapis.com/youtube/v3/search"
    EMBED_BASE = "https://www.youtube.com/embed/"

    def trailer_url(self, *, title: str) -> str | None:
        if not settings.YOUTUBE_API_KEY:
            return None
        params = {
            "key": settings.YOUTUBE_API_KEY,
            "q": f"{title} official trailer",
            "type": "video",
            "videoEmbeddable": "true",
            "maxResults": 1,
            "part": "snippet",
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(self.BASE, params=params)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("YouTube fetch failed: %s", exc)
            return None
        items = data.get("items") or []
        if not items:
            return None
        video_id = items[0]["id"].get("videoId")
        return f"{self.EMBED_BASE}{video_id}" if video_id else None


# ---------- module-level singletons ----------

books_client: CatalogueClient = BooksClient()
movies_client: CatalogueClient = MoviesClient()
articles_client: CatalogueClient = ArticlesClient()
youtube_client = YouTubeClient()


# ---------- test helpers ----------

class FakeCatalogueClient:
    """In-memory catalogue for tests — returns a fixed list shuffled deterministically."""

    def __init__(self, items: list[CatalogueItem]) -> None:
        self._items = items

    def search(self, *, query: str, mood: str | None = None, limit: int = 8) -> list[CatalogueItem]:
        rng = random.Random(hash(query) & 0xFFFFFFFF)
        copy = list(self._items)
        rng.shuffle(copy)
        return copy[:limit]


class FakeYouTubeClient:
    def __init__(self, url: str | None = "https://www.youtube.com/embed/fake123") -> None:
        self._url = url

    def trailer_url(self, *, title: str) -> str | None:
        return self._url
