"""Metrics Agent configuration.

All configurable values live in this module so they are not hardcoded
throughout the codebase. Every value can be overridden with an environment
variable (prefixed with ``MA_``), which keeps the application portable
between development and deployment environments without code changes.

Example:
    export MA_HOST=0.0.0.0
    export MA_PORT=8001
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
    app_name: str = os.getenv("MA_APP_NAME", "Metrics Agent")
    app_version: str = os.getenv("MA_APP_VERSION", "0.1.0")
    description: str = os.getenv(
        "MA_APP_DESCRIPTION",
        "Lightweight metrics agent that collects system metrics from Ubuntu servers.",
    )

    # --- Server ----------------------------------------------------------
    # Bind to 0.0.0.0 to allow connections from other machines.
    # This is safe on a private network. In production, use a reverse proxy.
    host: str = os.getenv("MA_HOST", "0.0.0.0")
    port: int = int(os.getenv("MA_PORT", "8001"))

    # --- API -------------------------------------------------------------
    api_prefix: str = os.getenv("MA_API_PREFIX", "/api")

    # --- Behaviour -------------------------------------------------------
    debug: bool = _env_bool("MA_DEBUG", False)


# A single shared instance used across the application.
settings = Settings()
