"""Health check endpoint.

Returns a simple JSON payload that proves the application is running
and reachable. Used by clients, load balancers and future CI/CD
deployment steps to verify the service is alive.
"""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Returns a simple JSON response indicating the application is running.",
)
async def health_check() -> dict:
    """Return a JSON payload confirming the application is healthy."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
