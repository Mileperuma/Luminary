"""Health check endpoint.

Used by the hosting platform (Render) as a liveness probe and by humans
to verify a deployment is up.
"""

from fastapi import APIRouter

from app import __version__

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return a simple liveness payload."""
    return {"status": "ok", "service": "luminary-backend", "version": __version__}
