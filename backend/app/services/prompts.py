"""Loader for the Markdown prompt templates under app/prompts/.

A template file looks like:

    # name

    ## System
    <system prompt>

    ## Example user
    <one example>

    ## Example assistant
    <one example>

We only need the System block at runtime — the examples exist so a
non-developer can read and tweak the template without breaking it.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

_SYSTEM_HEADER_RE = re.compile(r"^##\s+System\s*$", re.MULTILINE)
_NEXT_HEADER_RE = re.compile(r"^##\s+", re.MULTILINE)


@lru_cache(maxsize=64)
def load_system_prompt(name: str) -> str:
    """Return the body of the `## System` section of the named template."""
    path = _PROMPTS_DIR / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    m = _SYSTEM_HEADER_RE.search(text)
    if not m:
        raise ValueError(f"prompt '{name}' has no `## System` block")
    after_header = text[m.end():]
    next_match = _NEXT_HEADER_RE.search(after_header)
    body = after_header[: next_match.start()] if next_match else after_header
    return body.strip()
