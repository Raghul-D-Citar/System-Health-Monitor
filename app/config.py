"""Application configuration.

All configurable values live in this module so they are not hardcoded
throughout the codebase. Every value can be overridden with an environment
variable (prefixed with ``SHM_``), which keeps the application portable
between development and deployment environments without code changes.

Example:
    export SHM_HOST=0.0.0.0
    export SHM_PORT=8080
"""

import os


def _env_bool(name: str, default: bool) -> bool:
    """Read an environment variable and interpret it as a boolean."""
    raw = os.getenv(name, str(default))
    return raw.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    """Central place for application settings.

    Read once when the module is imported and exposed as ``settings``.
    """

    # --- Application metadata -------------------------------------------
    app_name: str = os.getenv("SHM_APP_NAME", "System Health Monitor")
    app_version: str = os.getenv("SHM_APP_VERSION", "0.1.0")
    description: str = os.getenv(
        "SHM_APP_DESCRIPTION",
        "Monitor performance metrics of Linux servers through a web dashboard.",
    )

    # --- Server ----------------------------------------------------------
    # Bind to localhost by default. The application is NOT exposed to
    # external clients yet; Nginx will act as the reverse proxy in a later
    # phase.
    host: str = os.getenv("SHM_HOST", "127.0.0.1")
    port: int = int(os.getenv("SHM_PORT", "8000"))

    # --- API -------------------------------------------------------------
    api_prefix: str = os.getenv("SHM_API_PREFIX", "/api")

    # --- Behaviour -------------------------------------------------------
    debug: bool = _env_bool("SHM_DEBUG", False)

    # --- Metrics Agent Integration (Phase 3) ----------------------------
    # URL of the Metrics Agent running on the monitored server.
    # Example: http://192.168.122.13:8001
    agent_url: str = os.getenv(
        "SHM_AGENT_URL",
        "http://127.0.0.1:8001",  # Default to localhost for development
    )
    # Timeout in seconds for requests to the Metrics Agent.
    agent_timeout: float = float(os.getenv("SHM_AGENT_TIMEOUT", "5.0"))


# A single shared instance used across the application.
settings = Settings()
