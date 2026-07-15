"""Chatbot service — runs the onboarding conversation and the general assistant.

Key responsibilities:
- Start a chat_session row for a user.
- Persist every user/assistant message.
- Call the LLM with the right system prompt and the full message history.
- Detect the JSON "finish" line emitted by the onboarding prompt, write the
  captured preferences to the database, and mark the session ended.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from app.models.chat import ChatMessage, ChatRole, ChatSession, ChatSessionType
from app.models.preference import MediaType, Preference, PreferenceSource
from app.models.user import User
from app.services import llm_client as _llm_module
from app.services.llm_client import LLMClient
from app.services.prompts import load_system_prompt

log = logging.getLogger("luminary.chat")

# Matches an entire JSON object on a line by itself (most permissive form).
_FINISH_LINE_RE = re.compile(r"\{[^\n]*\"action\"\s*:\s*\"finish\"[^\n]*\}")

MAX_TURNS = 10


@dataclass
class ChatReply:
    session_id: UUID
    assistant_message: str
    finished: bool
    captured_preferences: int = 0


def start_session(
    session: Session,
    *,
    user: User,
    session_type: ChatSessionType = ChatSessionType.GENERAL,
) -> ChatSession:
    chat_session = ChatSession(user_id=user.id, session_type=session_type)
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session


def _load_history(session: Session, *, chat_session_id: UUID) -> list[dict]:
    rows = list(session.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == chat_session_id)
        .order_by(ChatMessage.created_at)  # type: ignore[arg-type]
    ))
    return [{"role": r.role.value, "content": r.content} for r in rows]


def _system_prompt_for(chat_session: ChatSession) -> str:
    if chat_session.session_type == ChatSessionType.ONBOARDING:
        return load_system_prompt("onboarding_chat")
    return (
        "You are Luminary, a calm reading and viewing assistant. Answer the user's "
        "questions about their picks and preferences in plain, warm language. "
        "Keep replies short."
    )


def _extract_finish_payload(text: str) -> dict | None:
    m = _FINISH_LINE_RE.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        log.warning("LLM emitted finish-shaped JSON that failed to parse: %s", m.group(0))
        return None


def _save_captured_preferences(
    session: Session,
    *,
    user: User,
    payload: dict,
) -> int:
    rows = payload.get("preferences") or []
    saved = 0
    for r in rows:
        try:
            media_type = MediaType(r["media_type"])
            key = str(r["key"])
            value = str(r["value"])
            weight = float(r.get("weight", 0.5))
        except (KeyError, ValueError, TypeError) as exc:
            log.warning("skipping malformed preference row %s: %s", r, exc)
            continue
        pref = Preference(
            user_id=user.id,
            media_type=media_type,
            key=key,
            value=value,
            weight=max(-1.0, min(1.0, weight)),
            source=PreferenceSource.CHAT,
        )
        session.add(pref)
        saved += 1

    if saved and not user.onboarding_complete:
        user.onboarding_complete = True
        session.add(user)

    session.commit()

    # Refresh the profile vector for every media type that changed.
    if saved:
        changed_media: set[MediaType] = set()
        for r in rows:
            try:
                changed_media.add(MediaType(r["media_type"]))
            except (KeyError, ValueError, TypeError):
                continue
        try:
            from app.services.vector_memory import rebuild_user_embedding
            for m in changed_media:
                rebuild_user_embedding(session, user_id=user.id, media_type=m)
        except Exception as exc:  # noqa: BLE001
            log.warning("preference vector rebuild failed: %s", exc)

    return saved


def send_message(
    session: Session,
    *,
    user: User,
    chat_session: ChatSession,
    content: str,
    llm: LLMClient | None = None,
) -> ChatReply:
    # Resolve via the module (not the imported name) so tests can patch
    # llm_client.llm_client and have it actually take effect here.
    llm = llm or _llm_module.llm_client

    # Persist user's message
    user_msg = ChatMessage(
        session_id=chat_session.id,
        role=ChatRole.USER,
        content=content,
    )
    session.add(user_msg)
    session.commit()

    history = _load_history(session, chat_session_id=chat_session.id)

    # Enforce the 10-turn cap (LLM-side; user-side caps live in the API layer)
    assistant_turn_count = sum(1 for m in history if m["role"] == "assistant")
    if assistant_turn_count >= MAX_TURNS:
        forced = "Thanks — that's enough for me to build your profile. Saving it now."
        forced_payload = {"action": "finish", "preferences": []}
        reply_text = f"{forced}\n{json.dumps(forced_payload)}"
    else:
        system = _system_prompt_for(chat_session)
        reply_text = llm.chat(system, history)

    # Persist assistant's reply
    assistant_msg = ChatMessage(
        session_id=chat_session.id,
        role=ChatRole.ASSISTANT,
        content=reply_text,
    )
    session.add(assistant_msg)
    session.commit()

    # Look for the structured finish payload
    payload = _extract_finish_payload(reply_text)
    finished = False
    captured = 0
    visible_text = reply_text
    if payload is not None:
        finished = True
        captured = _save_captured_preferences(session, user=user, payload=payload)
        chat_session.ended_at = datetime.now(UTC)
        session.add(chat_session)
        session.commit()
        # Strip the JSON line from what we send back to the user.
        visible_text = _FINISH_LINE_RE.sub("", reply_text).strip()

    return ChatReply(
        session_id=chat_session.id,
        assistant_message=visible_text,
        finished=finished,
        captured_preferences=captured,
    )
