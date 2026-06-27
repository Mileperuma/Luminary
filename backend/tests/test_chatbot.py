"""Tests for the chatbot service — onboarding finish-detection in particular."""

import json

from sqlmodel import Session, select

from app.models.chat import ChatRole, ChatSession, ChatSessionType
from app.models.preference import Preference
from app.models.user import User
from app.services.chatbot import send_message, start_session


class _ScriptedLLM:
    """An LLM that returns a fixed list of replies in order."""

    def __init__(self, replies: list[str]) -> None:
        self._replies = list(replies)
        self.received: list[list[dict]] = []

    def chat(self, system: str, messages: list) -> str:
        self.received.append(list(messages))
        return self._replies.pop(0) if self._replies else "(no more scripted replies)"

    def summarise(self, text: str, *, max_words: int = 80) -> str:  # pragma: no cover
        return ""

    def explain_recommendation(self, profile_summary: str, item: dict) -> str:  # pragma: no cover
        return ""


def _make_user(session: Session) -> User:
    from app.core.security import hash_password
    user = User(email="alice@example.com", password_hash=hash_password("pw-1234567"), display_name="Alice")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_start_onboarding_session_creates_row(session: Session) -> None:
    user = _make_user(session)
    chat = start_session(session, user=user, session_type=ChatSessionType.ONBOARDING)
    assert chat.id is not None
    assert chat.session_type == ChatSessionType.ONBOARDING


def test_send_message_persists_both_messages(session: Session) -> None:
    user = _make_user(session)
    chat = start_session(session, user=user, session_type=ChatSessionType.GENERAL)
    llm = _ScriptedLLM(["Tell me more about that."])

    reply = send_message(session, user=user, chat_session=chat, content="I love Tana French.", llm=llm)

    from app.models.chat import ChatMessage
    rows = list(session.exec(select(ChatMessage).where(ChatMessage.session_id == chat.id)))
    assert len(rows) == 2
    assert rows[0].role == ChatRole.USER
    assert rows[1].role == ChatRole.ASSISTANT
    assert reply.assistant_message == "Tell me more about that."
    assert reply.finished is False


def test_onboarding_finish_payload_writes_preferences_and_marks_user(session: Session) -> None:
    user = _make_user(session)
    chat = start_session(session, user=user, session_type=ChatSessionType.ONBOARDING)

    payload = {
        "action": "finish",
        "preferences": [
            {"media_type": "book", "key": "genre", "value": "historical fiction", "weight": 0.9},
            {"media_type": "movie", "key": "tone", "value": "slow-burn", "weight": 0.8},
            {"media_type": "article", "key": "topic", "value": "culture", "weight": 0.6},
        ],
    }
    reply_text = f"Got it — saving your profile now.\n{json.dumps(payload)}"
    llm = _ScriptedLLM([reply_text])

    reply = send_message(session, user=user, chat_session=chat, content="that's enough", llm=llm)

    assert reply.finished is True
    assert reply.captured_preferences == 3
    # JSON line is stripped from the user-visible response
    assert "\"action\":\"finish\"" not in reply.assistant_message
    assert "saving your profile" in reply.assistant_message.lower()

    saved = list(session.exec(select(Preference).where(Preference.user_id == user.id)))
    assert len(saved) == 3
    assert {p.value for p in saved} == {"historical fiction", "slow-burn", "culture"}

    session.refresh(user)
    assert user.onboarding_complete is True


def test_finish_with_malformed_rows_skips_them(session: Session) -> None:
    user = _make_user(session)
    chat = start_session(session, user=user, session_type=ChatSessionType.ONBOARDING)
    payload = {
        "action": "finish",
        "preferences": [
            {"media_type": "book", "key": "genre", "value": "thrillers", "weight": 0.7},
            {"media_type": "INVALID", "key": "genre", "value": "x"},
            {"this": "isn't a preference at all"},
        ],
    }
    reply_text = f"Done.\n{json.dumps(payload)}"
    llm = _ScriptedLLM([reply_text])

    reply = send_message(session, user=user, chat_session=chat, content="that's enough", llm=llm)

    assert reply.finished is True
    assert reply.captured_preferences == 1  # only the valid one was saved


# ---------- endpoints ----------

def test_chat_endpoint_round_trip(logged_in_client) -> None:
    client, headers = logged_in_client

    start = client.post("/api/chat/start", headers=headers, json={"session_type": "general"})
    assert start.status_code == 201, start.text
    session_id = start.json()["session_id"]
    assert "how can i help" in start.json()["opening_message"].lower()

    # Stub the module-level LLM
    from app.services import llm_client
    original = llm_client.llm_client
    llm_client.llm_client = _ScriptedLLM(["Sure — happy to chat."])
    try:
        res = client.post(
            "/api/chat/message",
            headers=headers,
            json={"session_id": session_id, "content": "what's good?"},
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["session_id"] == session_id
        assert body["assistant_message"] == "Sure — happy to chat."
        assert body["finished"] is False
    finally:
        llm_client.llm_client = original


def test_chat_message_to_unknown_session_returns_404(logged_in_client) -> None:
    client, headers = logged_in_client
    res = client.post(
        "/api/chat/message",
        headers=headers,
        json={"session_id": "00000000-0000-0000-0000-000000000000", "content": "hi"},
    )
    assert res.status_code == 404


def test_chat_message_to_another_users_session_returns_404(session: Session, logged_in_client) -> None:
    client, headers = logged_in_client

    # Create a session for a DIFFERENT user — that should be invisible.
    from app.core.security import hash_password
    other = User(email="bob@example.com", password_hash=hash_password("pw-1234567"), display_name="Bob")
    session.add(other)
    session.commit()
    session.refresh(other)
    other_chat = ChatSession(user_id=other.id, session_type=ChatSessionType.GENERAL)
    session.add(other_chat)
    session.commit()
    session.refresh(other_chat)

    res = client.post(
        "/api/chat/message",
        headers=headers,
        json={"session_id": str(other_chat.id), "content": "hi"},
    )
    assert res.status_code == 404
