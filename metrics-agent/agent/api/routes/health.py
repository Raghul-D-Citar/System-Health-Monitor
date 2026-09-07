"""Health check endpoint.

Returns a simple JSON payload that proves the Metrics Agent is running
and reachable.
"""

from fastapi import APIRouter

from agent.config import settings
from agent.models import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Returns a simple JSON response indicating the Metrics Agent is running.",
    response_model=HealthResponse,
)
async def health_check() -> HealthResponse:
    """Return a JSON payload confirming the Metrics Agent is healthy."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )
