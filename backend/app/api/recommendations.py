"""Recommendation endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.recommendation import RecommendationPublic, RecommendationRequest
from app.services.recommender import (
    RecommendationUnavailableError,
    recommend,
)

router = APIRouter()


@router.post("", response_model=RecommendationPublic, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    payload: RecommendationRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> RecommendationPublic:
    try:
        rec = recommend(
            session,
            user_id=current_user.id,
            media_type=payload.media_type,
            mood=payload.mood,
        )
    except RecommendationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"no recommendations available for {payload.media_type.value} right now",
        ) from exc
    return RecommendationPublic.model_validate(rec.model_dump())


@router.get("/{recommendation_id}", response_model=RecommendationPublic)
def get_recommendation(
    recommendation_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> RecommendationPublic:
    from app.models.recommendation import Recommendation

    rec = session.get(Recommendation, recommendation_id)
    if rec is None or rec.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="recommendation not found")
    return RecommendationPublic.model_validate(rec.model_dump())
