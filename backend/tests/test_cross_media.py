"""Tests for the cross-media linking service + endpoint."""

from uuid import UUID

from sqlmodel import Session

from app.core.security import hash_password
from app.models.preference import MediaType
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.catalogue import CatalogueItem, FakeCatalogueClient
from app.services.cross_media import find_related
from app.services.llm_client import FakeLLMClient


def _make_user_and_seed(session: Session, media_type: MediaType) -> tuple[User, Recommendation]:
    user = User(email="alice@example.com", password_hash=hash_password("pw-1234567"), display_name="Alice")
    session.add(user)
    session.commit()
    session.refresh(user)

    rec = Recommendation(
        user_id=user.id,
        media_type=media_type,
        external_id="seed:1",
        title="Gone Girl",
        description="A psychological thriller about a missing wife.",
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return user, rec


def test_find_related_returns_one_per_other_media(session: Session) -> None:
    _, rec = _make_user_and_seed(session, MediaType.BOOK)

    from app.services import catalogue
    original_movies = catalogue.movies_client
    original_articles = catalogue.articles_client
    catalogue.movies_client = FakeCatalogueClient([
        CatalogueItem(MediaType.MOVIE, "tmdb:1", "Gone Girl (film)", "Adaptation", "img"),
    ])
    catalogue.articles_client = FakeCatalogueClient([
        CatalogueItem(MediaType.ARTICLE, "guardian:abc", "The Real Gone Girl", "Longread", "img"),
    ])

    try:
        related = find_related(rec, llm=FakeLLMClient("psychological thriller missing"))
    finally:
        catalogue.movies_client = original_movies
        catalogue.articles_client = original_articles

    assert set(related.keys()) == {"movie", "article"}
    assert related["movie"].title == "Gone Girl (film)"
    assert related["article"].title == "The Real Gone Girl"


def test_find_related_omits_media_with_no_results(session: Session) -> None:
    _, rec = _make_user_and_seed(session, MediaType.MOVIE)

    from app.services import catalogue
    original_books = catalogue.books_client
    original_articles = catalogue.articles_client
    catalogue.books_client = FakeCatalogueClient([
        CatalogueItem(MediaType.BOOK, "gbooks:1", "Source Material", "Inspired the film", "img"),
    ])
    catalogue.articles_client = FakeCatalogueClient([])  # nothing back

    try:
        related = find_related(rec, llm=FakeLLMClient("thriller"))
    finally:
        catalogue.books_client = original_books
        catalogue.articles_client = original_articles

    assert "book" in related
    assert "article" not in related


# ---------- endpoint ----------

def test_cross_media_endpoint_returns_related_items(logged_in_client) -> None:
    client, headers = logged_in_client

    from app.api.deps import get_session
    from app.main import app
    session = next(app.dependency_overrides[get_session]())

    me = client.get("/api/auth/me", headers=headers).json()
    rec = Recommendation(
        user_id=UUID(me["id"]),
        media_type=MediaType.BOOK,
        external_id="seed:42",
        title="Gone Girl",
        description="thriller",
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)

    from app.services import catalogue, llm_client
    original_movies = catalogue.movies_client
    original_articles = catalogue.articles_client
    original_llm = llm_client.llm_client
    catalogue.movies_client = FakeCatalogueClient([
        CatalogueItem(MediaType.MOVIE, "tmdb:1", "Gone Girl (film)", "Adaptation", "img"),
    ])
    catalogue.articles_client = FakeCatalogueClient([
        CatalogueItem(MediaType.ARTICLE, "guardian:abc", "Long read", "About the case", "img"),
    ])
    llm_client.llm_client = FakeLLMClient("thriller missing")

    try:
        res = client.get(f"/api/recommendations/{rec.id}/cross-media", headers=headers)
    finally:
        catalogue.movies_client = original_movies
        catalogue.articles_client = original_articles
        llm_client.llm_client = original_llm

    assert res.status_code == 200, res.text
    body = res.json()
    assert set(body.keys()) == {"movie", "article"}
    assert body["movie"]["title"] == "Gone Girl (film)"


def test_cross_media_endpoint_404_for_unknown_recommendation(logged_in_client) -> None:
    client, headers = logged_in_client
    res = client.get(
        "/api/recommendations/00000000-0000-0000-0000-000000000000/cross-media",
        headers=headers,
    )
    assert res.status_code == 404


def test_cross_media_endpoint_404_for_other_users_recommendation(session: Session, logged_in_client) -> None:
    client, headers = logged_in_client

    other = User(email="bob@example.com", password_hash=hash_password("pw-1234567"), display_name="Bob")
    session.add(other)
    session.commit()
    session.refresh(other)
    rec = Recommendation(
        user_id=other.id, media_type=MediaType.BOOK,
        external_id="seed:99", title="X", description="y",
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)

    res = client.get(f"/api/recommendations/{rec.id}/cross-media", headers=headers)
    assert res.status_code == 404
