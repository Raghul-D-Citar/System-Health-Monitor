"""Development runner.

Starts the FastAPI application with Uvicorn using the values from the
application configuration (``app/config.py``).

Usage:
    python run.py
"""

import uvicorn

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
