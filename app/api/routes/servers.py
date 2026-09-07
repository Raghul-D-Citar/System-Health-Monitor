"""Server metrics endpoint (Phase 3).

Fetches metrics from a Metrics Agent running on a monitored Ubuntu server.
The agent URL is configured via the SHM_AGENT_URL environment variable.
"""

import httpx
from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter()


@router.get(
    "/servers/{server_id}/metrics",
    tags=["servers"],
    summary="Get metrics from a server",
    description="Fetches system metrics from a Metrics Agent running on a monitored server.",
)
async def get_server_metrics(server_id: str) -> dict:
    """Fetch metrics from a Metrics Agent.

    Args:
        server_id: Identifier for the server (for future multi-server support).
                   Currently, all requests go to the configured agent URL.

    Returns:
        dict: Metrics response from the Metrics Agent (CPU, memory, disk, network, system).

    Raises:
        HTTPException: If the Metrics Agent is unreachable or returns an error.
    """
    # For Phase 3, we ignore server_id and always query the configured agent URL.
    # Future phases will support multiple agents with a registry mapping server_id to URLs.

    agent_url = settings.agent_url
    timeout = settings.agent_timeout
    metrics_endpoint = f"{agent_url}/api/metrics"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                metrics_endpoint,
                timeout=timeout,
            )

            # If the Metrics Agent returned an error, return the error as-is.
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Metrics Agent returned status {response.status_code}: {response.text}",
                )

            # Return the metrics from the agent.
            return response.json()

    except HTTPException:
        # Re-raise HTTPException as-is (don't catch it with the generic handler)
        raise
    except httpx.ConnectError as e:
        # Connection refused, connection reset, or similar network error.
        raise HTTPException(
            status_code=503,
            detail=f"Cannot reach Metrics Agent at {agent_url}: {str(e)}",
        )
    except httpx.TimeoutException as e:
        # Request timed out.
        raise HTTPException(
            status_code=504,
            detail=f"Request to Metrics Agent timed out after {timeout}s: {str(e)}",
        )
    except httpx.HTTPError as e:
        # Generic httpx error (client errors, invalid response, etc.).
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with Metrics Agent: {str(e)}",
        )
    except ValueError as e:
        # JSON decode error or similar.
        raise HTTPException(
            status_code=502,
            detail=f"Metrics Agent returned invalid JSON: {str(e)}",
        )
    except Exception as e:
        # Catch-all for unexpected errors.
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while fetching metrics: {str(e)}",
        )
