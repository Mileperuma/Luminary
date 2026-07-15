"""Digest opt-in endpoint."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/opt-in")
def opt_in(current_user: CurrentUser, session: SessionDep) -> dict[str, bool]:
    current_user.digest_opt_in = True
    session.add(current_user)
    session.commit()
    return {"digest_opt_in": True}


@router.post("/opt-out")
def opt_out(current_user: CurrentUser, session: SessionDep) -> dict[str, bool]:
    current_user.digest_opt_in = False
    session.add(current_user)
    session.commit()
    return {"digest_opt_in": False}
