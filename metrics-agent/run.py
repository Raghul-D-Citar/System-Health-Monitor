"""Development runner for the Metrics Agent.

Starts the FastAPI application with Uvicorn using the values from the
application configuration (``agent/config.py``).

Usage:
    python run.py
"""

import uvicorn

from agent.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "agent.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
