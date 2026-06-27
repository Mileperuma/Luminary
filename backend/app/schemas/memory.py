"""Schema for the returning-user welcome payload."""

from typing import Any

from pydantic import BaseModel


class WelcomeResponse(BaseModel):
    greeting: str
    is_returning: bool
    needs_onboarding: bool
    fresh_picks: list[dict[str, Any]]
