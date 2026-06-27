"""Feedback endpoint — POST /api/feedback."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.feedback import FeedbackCreate, FeedbackPublic
from app.services.feedback import RecommendationNotFoundError, record_feedback

router = APIRouter()


@router.post("", response_model=FeedbackPublic, status_code=status.HTTP_201_CREATED)
def post_feedback(
    payload: FeedbackCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> FeedbackPublic:
    try:
        fb, delta = record_feedback(
            session,
            user_id=current_user.id,
            recommendation_id=payload.recommendation_id,
            kind=payload.kind,
        )
    except RecommendationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="recommendation not found",
        ) from exc
    return FeedbackPublic(
        id=fb.id,
        recommendation_id=fb.recommendation_id,
        kind=fb.kind,
        created_at=fb.created_at,
        preference_delta=delta,
    )
