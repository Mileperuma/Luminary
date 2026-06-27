"""Preferences CRUD endpoints — list, bulk-create, update, delete."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models.preference import Preference, PreferenceSource
from app.schemas.preference import (
    PreferencePublic,
    PreferencesBulkCreate,
    PreferenceUpdate,
)

router = APIRouter()


@router.get("", response_model=list[PreferencePublic])
def list_preferences(current_user: CurrentUser, session: SessionDep) -> list[PreferencePublic]:
    rows = list(session.exec(select(Preference).where(Preference.user_id == current_user.id)))
    return [PreferencePublic.model_validate(r.model_dump()) for r in rows]


@router.post("", response_model=list[PreferencePublic], status_code=status.HTTP_201_CREATED)
def bulk_create_preferences(
    payload: PreferencesBulkCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> list[PreferencePublic]:
    created: list[Preference] = []
    for p in payload.preferences:
        row = Preference(
            user_id=current_user.id,
            media_type=p.media_type,
            key=p.key,
            value=p.value,
            weight=p.weight,
            source=PreferenceSource.EXPLICIT,
        )
        session.add(row)
        created.append(row)
    session.commit()
    for row in created:
        session.refresh(row)
    return [PreferencePublic.model_validate(r.model_dump()) for r in created]


@router.patch("/{preference_id}", response_model=PreferencePublic)
def update_preference(
    preference_id: UUID,
    payload: PreferenceUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> PreferencePublic:
    pref = session.get(Preference, preference_id)
    if pref is None or pref.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="preference not found")
    if payload.value is not None:
        pref.value = payload.value
    if payload.weight is not None:
        pref.weight = payload.weight
    pref.source = PreferenceSource.EXPLICIT
    session.add(pref)
    session.commit()
    session.refresh(pref)
    return PreferencePublic.model_validate(pref.model_dump())


@router.delete("/{preference_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preference(
    preference_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    pref = session.get(Preference, preference_id)
    if pref is None or pref.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="preference not found")
    session.delete(pref)
    session.commit()
