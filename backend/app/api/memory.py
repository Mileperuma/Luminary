"""Memory endpoint — GET /api/memory/welcome."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.memory import WelcomeResponse
from app.services.memory import welcome

router = APIRouter()


@router.get("/welcome", response_model=WelcomeResponse)
def get_welcome(current_user: CurrentUser, session: SessionDep) -> WelcomeResponse:
    payload = welcome(session, user=current_user)
    return WelcomeResponse(
        greeting=payload.greeting,
        is_returning=payload.is_returning,
        needs_onboarding=payload.needs_onboarding,
        fresh_picks=payload.fresh_picks,
    )
