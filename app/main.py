"""Application entry point.

Creates the FastAPI application, registers the API routers and global
error handlers, and exposes the root endpoint.

Run with:  python run.py
       or  uvicorn app.main:app --host 127.0.0.1 --port 8000
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.health import router as health_router
from app.api.routes.servers import router as servers_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
)

# --- Routers ----------------------------------------------------------------
# Future phases add more routers here (metrics, systems, dashboard, ...).
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(servers_router, prefix=settings.api_prefix)


# --- Error handling ---------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Return HTTP errors as JSON instead of the default plain-text body."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch unexpected errors so clients always receive a JSON response."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# --- Routes -----------------------------------------------------------------
@app.get("/", tags=["root"], summary="API root")
async def root() -> dict:
    """Root endpoint pointing users to the docs and the health check."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "message": "System Health Monitor API is running.",
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
        "servers_metrics": f"{settings.api_prefix}/servers/{{server_id}}/metrics (Phase 3)",
    }
