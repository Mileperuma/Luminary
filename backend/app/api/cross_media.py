"""GET /api/recommendations/{recommendation_id}/cross-media."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.models.recommendation import Recommendation
from app.services.cross_media import find_related

router = APIRouter()


@router.get("/{recommendation_id}/cross-media")
def cross_media_for_recommendation(
    recommendation_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> dict[str, dict]:
    rec = session.get(Recommendation, recommendation_id)
    if rec is None or rec.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="recommendation not found")

    related = find_related(rec)
    return {media_type: item.to_dict() for media_type, item in related.items()}
