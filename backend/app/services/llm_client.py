"""LLM adapter — wraps Claude (primary) and OpenAI (fallback) behind one interface.

Why an adapter at all:
- Vendor SDKs leak through call sites otherwise.
- Tests can substitute a fake (`FakeLLMClient`) without monkey-patching SDKs.
- Switching to a different provider is one file, not a search-and-replace.

Cost control: every call records token usage in `_token_log` (in-memory for now
— Phase 2 moves it to Redis). If `LLM_DAILY_TOKEN_BUDGET` is exceeded, calls
fall back to a templated string so the demo never crashes from rate limits.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Protocol

import anthropic
import openai

from app.core.config import get_settings

log = logging.getLogger("luminary.llm")
settings = get_settings()


# ---------- public surface ----------

class LLMClient(Protocol):
    def chat(self, system: str, messages: list[dict]) -> str: ...
    def summarise(self, text: str, *, max_words: int = 80) -> str: ...
    def explain_recommendation(self, profile_summary: str, item: dict) -> str: ...


# ---------- shared state ----------

_token_log: dict[str, int] = defaultdict(int)  # date_iso -> tokens


def _today() -> str:
    return datetime.now(UTC).date().isoformat()


def _record_tokens(n: int) -> None:
    _token_log[_today()] += n


def _over_budget() -> bool:
    return _token_log[_today()] >= settings.LLM_DAILY_TOKEN_BUDGET


# ---------- implementations ----------

class _ClaudeClient:
    """Anthropic Claude. Used when ANTHROPIC_API_KEY is set."""

    def __init__(self, api_key: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)

    def chat(self, system: str, messages: list[dict]) -> str:
        resp = self._client.messages.create(
            model="claude-sonnet-4-5",
            system=system,
            messages=messages,
            max_tokens=1024,
        )
        _record_tokens(resp.usage.input_tokens + resp.usage.output_tokens)
        return resp.content[0].text  # type: ignore[union-attr]


class _OpenAIClient:
    """OpenAI. Used when ANTHROPIC_API_KEY is missing but OPENAI_API_KEY is set."""

    def __init__(self, api_key: str) -> None:
        self._client = openai.OpenAI(api_key=api_key)

    def chat(self, system: str, messages: list[dict]) -> str:
        full = [{"role": "system", "content": system}, *messages]
        resp = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=full,
            max_tokens=1024,
        )
        usage = resp.usage
        if usage:
            _record_tokens(usage.prompt_tokens + usage.completion_tokens)
        return resp.choices[0].message.content or ""


class _OfflineClient:
    """Used when no API keys are configured, when the daily budget is exceeded,
    or when the upstream provider raises. Returns a templated string so the
    demo always completes."""

    def chat(self, system: str, messages: list[dict]) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "your request",
        )
        return (
            "I'd love to recommend something here, but my recommendation engine is "
            "in offline mode right now. You asked about: "
            f"\"{last_user[:120]}\"."
        )


# ---------- facade ----------

class _Adapter:
    """Routes to the best available backend, with offline fallback."""

    def __init__(self) -> None:
        self._primary: object | None = None
        self._secondary: object | None = None
        if settings.ANTHROPIC_API_KEY:
            self._primary = _ClaudeClient(settings.ANTHROPIC_API_KEY)
        if settings.OPENAI_API_KEY:
            self._secondary = _OpenAIClient(settings.OPENAI_API_KEY)
        self._offline = _OfflineClient()

    def chat(self, system: str, messages: list[dict]) -> str:
        if _over_budget():
            log.warning("LLM daily budget exceeded; returning offline response")
            return self._offline.chat(system, messages)

        for client, name in ((self._primary, "claude"), (self._secondary, "openai")):
            if client is None:
                continue
            try:
                return client.chat(system, messages)  # type: ignore[attr-defined]
            except Exception as exc:  # noqa: BLE001
                log.warning("%s call failed: %s", name, exc)
                continue

        log.info("no LLM provider configured; returning offline response")
        return self._offline.chat(system, messages)

    def summarise(self, text: str, *, max_words: int = 80) -> str:
        system = (
            "You write short, warm, plain-language summaries. "
            f"Stay under {max_words} words. No marketing speak."
        )
        return self.chat(system, [{"role": "user", "content": text}])

    def explain_recommendation(self, profile_summary: str, item: dict) -> str:
        system = (
            "You are Luminary, a calm reading and viewing assistant. "
            "Write a single short paragraph (60-80 words) explaining why this "
            "item fits the user, in plain warm language. No marketing voice, no "
            "exclamation marks, no \"you'll love\". Reference one or two specific "
            "things from their profile."
        )
        item_blob = (
            f"Title: {item.get('title')}\n"
            f"Type: {item.get('media_type')}\n"
            f"Description: {item.get('description', '')[:600]}\n"
        )
        user_msg = (
            f"User profile:\n{profile_summary}\n\nItem to explain:\n{item_blob}"
        )
        return self.chat(system, [{"role": "user", "content": user_msg}])


# Module-level instance — import from this module, do not construct your own.
llm_client: LLMClient = _Adapter()


# ---------- test helpers ----------

class FakeLLMClient:
    """Deterministic stand-in for tests.

    Records every call on `calls` and returns predictable strings so tests can
    assert on routing without mocking the SDKs.
    """

    def __init__(self, explain_text: str = "This fits because you said you like X.") -> None:
        self.calls: list[dict] = []
        self._explain_text = explain_text

    def chat(self, system: str, messages: list[dict]) -> str:
        self.calls.append({"kind": "chat", "system": system, "messages": messages})
        return "fake-chat-response"

    def summarise(self, text: str, *, max_words: int = 80) -> str:
        self.calls.append({"kind": "summarise", "text": text, "max_words": max_words})
        return f"fake-summary({text[:30]}...)"

    def explain_recommendation(self, profile_summary: str, item: dict) -> str:
        self.calls.append({
            "kind": "explain",
            "profile_summary": profile_summary,
            "item": item,
        })
        return self._explain_text
