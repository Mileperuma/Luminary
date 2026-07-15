"""Tests for embeddings + vector-based ranking."""

from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.preference import MediaType, Preference, PreferenceSource
from app.models.preference_embedding import PreferenceEmbedding
from app.models.user import User
from app.services.catalogue import CatalogueItem
from app.services.embeddings import FakeEmbeddingClient
from app.services.vector_memory import rank_by_similarity, rebuild_user_embedding


def _user(session: Session) -> User:
    user = User(email="a@b.co", password_hash=hash_password("pw-1234567"), display_name="A")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_rebuild_creates_row_first_time(session: Session) -> None:
    user = _user(session)
    session.add(Preference(user_id=user.id, media_type=MediaType.MOVIE,
                           key="genre", value="thriller", weight=0.9,
                           source=PreferenceSource.CHAT))
    session.commit()

    fake = FakeEmbeddingClient([0.2] * 1536)
    rebuild_user_embedding(session, user_id=user.id, media_type=MediaType.MOVIE, client=fake)

    row = session.exec(select(PreferenceEmbedding)).first()
    assert row is not None
    assert row.embedding[0] == 0.2
    assert "thriller" in row.summary


def test_rebuild_updates_row_second_time(session: Session) -> None:
    user = _user(session)
    session.add(Preference(user_id=user.id, media_type=MediaType.MOVIE,
                           key="genre", value="thriller", weight=0.9,
                           source=PreferenceSource.CHAT))
    session.commit()

    rebuild_user_embedding(session, user_id=user.id, media_type=MediaType.MOVIE,
                           client=FakeEmbeddingClient([0.1] * 1536))
    rebuild_user_embedding(session, user_id=user.id, media_type=MediaType.MOVIE,
                           client=FakeEmbeddingClient([0.9] * 1536))

    rows = list(session.exec(select(PreferenceEmbedding)))
    assert len(rows) == 1  # updated, not duplicated
    assert rows[0].embedding[0] == 0.9


def test_rank_by_similarity_reorders_candidates(session: Session) -> None:
    user = _user(session)
    # Store a profile vector that is (1, 0, 0, ..., 0)
    profile = [1.0] + [0.0] * 1535
    session.add(PreferenceEmbedding(
        user_id=user.id, media_type=MediaType.MOVIE,
        embedding=profile, summary="test",
    ))
    session.commit()

    class DirectionalEmbedding:
        """Returns (1,0,..) for items whose title contains 'match', else (0,1,..)."""
        calls: list = []
        def embed(self, text: str) -> list[float]:
            self.calls.append(text)
            if "match" in text.lower():
                return [1.0] + [0.0] * 1535
            return [0.0, 1.0] + [0.0] * 1534

    fake = DirectionalEmbedding()

    candidates = [
        CatalogueItem(MediaType.MOVIE, "1", "Nope", "irrelevant"),
        CatalogueItem(MediaType.MOVIE, "2", "This is a match", "yes"),
        CatalogueItem(MediaType.MOVIE, "3", "Also nope", "not it"),
    ]
    ranked = rank_by_similarity(session, user_id=user.id, media_type=MediaType.MOVIE,
                                candidates=candidates, client=fake)
    assert ranked[0].external_id == "2"


def test_rank_returns_candidates_unchanged_when_no_profile(session: Session) -> None:
    user = _user(session)
    candidates = [
        CatalogueItem(MediaType.MOVIE, "1", "A", "x"),
        CatalogueItem(MediaType.MOVIE, "2", "B", "y"),
    ]
    ranked = rank_by_similarity(session, user_id=user.id, media_type=MediaType.MOVIE,
                                candidates=candidates, client=FakeEmbeddingClient())
    assert [c.external_id for c in ranked] == ["1", "2"]
