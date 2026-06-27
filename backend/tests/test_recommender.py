"""Tests for the recommender service and POST /api/recommendations.

Uses FakeCatalogueClient + FakeLLMClient so no network is involved.
"""

from sqlmodel import Session

from app.models.preference import MediaType, Preference, PreferenceSource
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.catalogue import (
    CatalogueItem,
    FakeCatalogueClient,
    FakeYouTubeClient,
)
from app.services.llm_client import FakeLLMClient
from app.services.recommender import RecommendationUnavailableError, recommend


def _seed_user(session: Session, *, email: str = "alice@example.com") -> User:
    from app.core.security import hash_password
    user = User(email=email, password_hash=hash_password("pw-1234567"), display_name="Alice")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _seed_preferences(session: Session, user: User) -> None:
    rows = [
        Preference(user_id=user.id, media_type=MediaType.MOVIE, key="genre",
                   value="psychological thriller", weight=0.9, source=PreferenceSource.CHAT),
        Preference(user_id=user.id, media_type=MediaType.MOVIE, key="tone",
                   value="slow-burn", weight=0.7, source=PreferenceSource.CHAT),
        Preference(user_id=user.id, media_type=MediaType.BOOK, key="genre",
                   value="historical fiction", weight=0.8, source=PreferenceSource.CHAT),
    ]
    for r in rows:
        session.add(r)
    session.commit()


def _fake_movies() -> FakeCatalogueClient:
    return FakeCatalogueClient([
        CatalogueItem(MediaType.MOVIE, "tmdb:1", "Gone Girl",
                      "A psychological thriller slow-burn.", "img1", keywords=["thriller"]),
        CatalogueItem(MediaType.MOVIE, "tmdb:2", "Toy Story",
                      "Family animation about toys.", "img2", keywords=["animation"]),
        CatalogueItem(MediaType.MOVIE, "tmdb:3", "Prisoners",
                      "A slow-burn psychological thriller about a kidnapping.",
                      "img3", keywords=["thriller"]),
        CatalogueItem(MediaType.MOVIE, "tmdb:4", "Mystic River", "A drama.",
                      "img4", keywords=["drama"]),
        CatalogueItem(MediaType.MOVIE, "tmdb:5", "Zodiac", "A psychological thriller.",
                      "img5", keywords=["thriller"]),
        CatalogueItem(MediaType.MOVIE, "tmdb:6", "Knives Out", "A whodunnit.",
                      "img6", keywords=["mystery"]),
    ])


# ---------- service ----------

def test_recommend_returns_a_relevant_primary_and_four_similars(session: Session) -> None:
    user = _seed_user(session)
    _seed_preferences(session, user)

    rec = recommend(
        session,
        user_id=user.id,
        media_type=MediaType.MOVIE,
        books=FakeCatalogueClient([]),
        movies=_fake_movies(),
        articles=FakeCatalogueClient([]),
        youtube=FakeYouTubeClient("https://example.com/embed/abc"),
        llm=FakeLLMClient("Fake explanation."),
    )

    assert rec.media_type == MediaType.MOVIE
    # primary should match a psychological thriller
    assert "thriller" in rec.title.lower() or "thriller" in rec.description.lower() \
           or rec.external_id in {"tmdb:1", "tmdb:3", "tmdb:5"}
    assert len(rec.similar_items) >= 4
    assert rec.trailer_url == "https://example.com/embed/abc"
    assert rec.description == "Fake explanation."


def test_recommend_persists_a_row(session: Session) -> None:
    user = _seed_user(session)
    _seed_preferences(session, user)
    rec = recommend(
        session,
        user_id=user.id,
        media_type=MediaType.MOVIE,
        books=FakeCatalogueClient([]),
        movies=_fake_movies(),
        articles=FakeCatalogueClient([]),
        youtube=FakeYouTubeClient(),
        llm=FakeLLMClient(),
    )
    from sqlmodel import select
    rows = list(session.exec(select(Recommendation).where(Recommendation.user_id == user.id)))
    assert len(rows) == 1
    assert rows[0].id == rec.id


def test_recommend_raises_when_no_candidates(session: Session) -> None:
    user = _seed_user(session)
    _seed_preferences(session, user)
    try:
        recommend(
            session,
            user_id=user.id,
            media_type=MediaType.MOVIE,
            books=FakeCatalogueClient([]),
            movies=FakeCatalogueClient([]),
            articles=FakeCatalogueClient([]),
            youtube=FakeYouTubeClient(),
            llm=FakeLLMClient(),
        )
    except RecommendationUnavailableError as exc:
        assert exc.media_type == MediaType.MOVIE
    else:
        raise AssertionError("expected RecommendationUnavailableError")


def test_cold_start_user_still_gets_a_recommendation(session: Session) -> None:
    """A user with no preferences should still receive a fallback pick."""
    user = _seed_user(session, email="newbie@example.com")
    rec = recommend(
        session,
        user_id=user.id,
        media_type=MediaType.MOVIE,
        books=FakeCatalogueClient([]),
        movies=_fake_movies(),
        articles=FakeCatalogueClient([]),
        youtube=FakeYouTubeClient(),
        llm=FakeLLMClient(),
    )
    assert rec.id is not None


# ---------- endpoint ----------

def test_post_recommendations_returns_201_and_full_payload(logged_in_client) -> None:
    client, headers = logged_in_client

    # Override the recommender by patching the singletons
    from app.services import catalogue, llm_client, recommender  # noqa: F401
    original_movies = catalogue.movies_client
    original_books = catalogue.books_client
    original_articles = catalogue.articles_client
    original_yt = catalogue.youtube_client
    original_llm = llm_client.llm_client

    catalogue.movies_client = _fake_movies()
    catalogue.books_client = FakeCatalogueClient([])
    catalogue.articles_client = FakeCatalogueClient([])
    catalogue.youtube_client = FakeYouTubeClient("https://example.com/embed/xyz")
    llm_client.llm_client = FakeLLMClient("Endpoint explanation.")

    try:
        res = client.post(
            "/api/recommendations",
            headers=headers,
            json={"media_type": "movie"},
        )
        assert res.status_code == 201, res.text
        body = res.json()
        assert body["media_type"] == "movie"
        assert len(body["similar_items"]) >= 4
        assert body["trailer_url"] == "https://example.com/embed/xyz"
        assert body["description"] == "Endpoint explanation."
    finally:
        catalogue.movies_client = original_movies
        catalogue.books_client = original_books
        catalogue.articles_client = original_articles
        catalogue.youtube_client = original_yt
        llm_client.llm_client = original_llm


def test_post_recommendations_without_token_returns_401(client) -> None:
    res = client.post("/api/recommendations", json={"media_type": "movie"})
    assert res.status_code == 401
