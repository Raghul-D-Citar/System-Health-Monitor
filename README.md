# System Health Monitor

Monitor the performance metrics of one or more Linux servers and display
them through a web dashboard.

> **Phase 1: Project Foundation** — this is the first phase of a
> multi-phase build. Only the foundation described below is implemented.
> Nothing else exists yet. See [Current Phase](#current-phase) and
> [Future Phases](#future-phases).

---

## Project Objective

The goal is to build a production-style application that:

1. Collects performance metrics from one or more Linux servers:
   CPU, RAM, disk, network, system information and uptime.
2. Exposes those metrics through a FastAPI backend.
3. Displays them in a web dashboard built with React + TypeScript.
4. Is delivered through a CI/CD pipeline (GitHub + Jenkins) to a Linux VM,
   with Nginx acting as a reverse proxy in front of the application.

The project is built **phase by phase**. Phase 1 only lays the foundation:
a clean, runnable FastAPI skeleton with configuration, tests and
documentation. **No monitoring functionality exists yet.**

## Current Architecture

Phase 1 delivers the foundation of the following architecture. The
components marked *(future)* are planned but **not implemented yet**:

```
Client
  |
  v
Nginx Reverse Proxy (future)
  |
  v
FastAPI Backend            <-- implemented as a skeleton (Phase 1)
  |
  v
System Metrics Collector (future)
  |
  +--> CPU      (future)
  +--> RAM      (future)
  +--> Disk     (future)
  +--> Network  (future)
  +--> System information (future)
  +--> Uptime   (future)
  |
  v
Dashboard (future)
```

What exists today is the FastAPI backend skeleton: it starts, serves a
health check at `GET /api/health`, and returns JSON for every response
(including errors). It binds to `127.0.0.1` only — it is **not** exposed
to external clients.

## Technology Stack

| Layer              | Technology                                          | Status        |
| ------------------ | --------------------------------------------------- | ------------- |
| Backend            | Python + FastAPI + Uvicorn                          | Phase 1 (skeleton) |
| Frontend           | HTML + CSS + Vanilla JavaScript                     | Future        |
| Reverse proxy      | Nginx                                               | Future        |
| CI/CD              | Jenkins + GitHub + GitHub Webhooks                  | Future        |
| Testing            | pytest + curl                                       | Phase 1 (health test) |
| Version control    | Git + GitHub                                        | Phase 1 (local repo) |
| Deployment         | Linux VM (no cloud account)                         | Future        |

## Project Directory Structure

```
system-health-monitor/
├── .gitignore                  # Ignored files (Python, Linux, IDEs, project)
├── README.md                   # This file
├── requirements.txt            # Runtime dependencies (fastapi, uvicorn)
├── requirements-dev.txt        # Dev/test dependencies (pytest, httpx)
├── run.py                      # Development runner (reads app/config.py)
├── app/                        # Application package
│   ├── __init__.py
│   ├── config.py               # Central configuration (env-var driven)
│   ├── main.py                 # FastAPI app: routers + error handlers
│   └── api/
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           └── health.py       # GET /api/health endpoint
├── frontend/                   # Phase 4 dashboard (React + TypeScript)
└── tests/
  └── test_health.py          # pytest tests for the health endpoint
```

Notes on the layout:

- `app/` holds all application code; `app/main.py` is the only file that
  creates the FastAPI app.
- Routes live under `app/api/routes/` so future endpoints (metrics, systems,
  dashboard) each get their own module instead of piling up in `main.py`.
- `app/config.py` is the single place for configuration values, so nothing
  is hardcoded across the codebase.
- `tests/` mirrors the structure of `app/`.

## Setup Instructions

Prerequisites:

- A Linux machine (or VM) with Python 3.11+ installed.
- Git installed.
- No cloud account required — everything runs locally on your VM.

### 1. Clone or copy the project

```bash
git clone <your-repo-url> system-health-monitor
cd system-health-monitor
```

### 2. Create and activate the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your prompt should now show `(.venv)` at the start.

> The virtual environment keeps project dependencies isolated from the
> rest of your system. It is ignored by Git (see `.gitignore`).

To leave the virtual environment later:

```bash
deactivate
```

### 3. Install dependencies

Runtime dependencies:

```bash
pip install -r requirements.txt
```

Development and test dependencies (includes the runtime ones):

```bash
pip install -r requirements-dev.txt
```

### 4. Run the FastAPI application

```bash
python run.py
```

The app starts on `http://127.0.0.1:8000` (localhost only). You should see
output similar to:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Alternative (equivalent) command:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 5. Test the health endpoint

In a second terminal:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected output:

```json
{"status":"ok","service":"System Health Monitor","version":"0.1.0"}
```

Other useful endpoints:

| Endpoint               | Description                                        |
| ---------------------- | -------------------------------------------------- |
| `GET /`                | Root endpoint with links to docs and health check  |
| `GET /api/health`      | Health check (JSON)                                |
| `GET /docs`            | Interactive API documentation (Swagger UI)         |

Interactive docs are available at `http://127.0.0.1:8000/docs` — you can
call the health endpoint directly from your browser.

### 6. Run the tests

```bash
python -m pytest -v
```

Expected output:

```
tests/test_health.py::test_health_endpoint_returns_ok_status PASSED      [ 25%]
tests/test_health.py::test_health_endpoint_returns_json_content_type PASSED [ 50%]
tests/test_health.py::test_root_endpoint_is_reachable PASSED             [ 75%]
tests/test_health.py::test_unknown_endpoint_returns_json_404 PASSED      [100%]

=============================== 4 passed in 0.47s ===============================
```

### Configuration

All configuration lives in `app/config.py` and can be overridden with
environment variables (prefix `SHM_`). Example:

```bash
SHM_PORT=8080 python run.py      # run on port 8080 instead of 8000
```

Available variables:

| Variable               | Default                  | Purpose                        |
| ---------------------- | ------------------------ | ------------------------------ |
| `SHM_APP_NAME`         | `System Health Monitor`  | Application display name       |
| `SHM_APP_VERSION`      | `0.1.0`                  | Application version            |
| `SHM_APP_DESCRIPTION`  | (see `app/config.py`)    | Shown in the API docs          |
| `SHM_HOST`             | `127.0.0.1`              | Bind address (localhost only)  |
| `SHM_PORT`             | `8000`                   | Bind port                      |
| `SHM_API_PREFIX`       | `/api`                   | Prefix for all API routes      |
| `SHM_DEBUG`            | `false`                  | Enable debug/reload mode       |

---

## Phase 2 — Metrics Agent

**Status**: COMPLETE. A lightweight metrics collection agent has been
implemented that runs on Ubuntu servers and exposes system metrics through
a REST API.

### Objective

Build a separate, lightweight FastAPI Metrics Agent that:

1. Runs on an Ubuntu Server VM (separate from the Monitoring Server).
2. Collects system metrics from its own host using `psutil`.
3. Exposes those metrics through HTTP endpoints.
4. Can be accessed from other machines on the network.
5. Is thoroughly tested with pytest (mocked `psutil` dependencies).
6. Is configurable through environment variables.

In a future phase (Phase 3), the Monitoring Server will call this agent
to retrieve metrics. For now, the agent runs independently and can be
tested in isolation.

### Architecture

```
Ubuntu Server (Monitored Machine)
        |
        v
   Metrics Agent (FastAPI)
        |
        +-- GET /api/health           (Health check)
        |
        +-- GET /api/metrics          (All metrics)
        |
        +-- GET /api/metrics/cpu      (CPU metrics)
        +-- GET /api/metrics/memory   (Memory metrics)
        +-- GET /api/metrics/disk     (Disk metrics)
        +-- GET /api/metrics/network  (Network metrics)
        +-- GET /api/metrics/system   (System info)
        |
        v
     psutil
        |
  ┌─────┼─────┬──────────┬────────┐
  v     v     v          v        v
 CPU  RAM   Disk     Network    System
```

### Why a Separate Metrics Agent?

1. **Separation of Concerns**: The Monitoring Server focuses on aggregation
   and the dashboard. Metric collection is handled by a separate agent.
2. **Scalability**: Multiple Ubuntu servers can each run their own agent.
   The Monitoring Server queries all of them.
3. **Lightweight**: The agent is minimal and has few dependencies (just
   `fastapi`, `uvicorn`, and `psutil`).
4. **Network Isolation**: Each server reports only its own metrics. No
   database connection needed.
5. **Testable**: The agent can be tested in isolation before integrating
   with the Monitoring Server.

### Ubuntu Server Setup

Before starting the agent, ensure:

1. Ubuntu Server has Python 3.11+ installed.
2. The server is reachable from the Monitoring Server via its IP address.
3. No firewall blocks port 8001 (or the configured port).

Example setup on Ubuntu Server:

```bash
# Install Python if not present
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Clone or copy the project
cd /opt
git clone <your-repo-url> metrics-agent
cd metrics-agent

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Installation Commands

On the Ubuntu Server:

```bash
# Navigate to the metrics-agent directory
cd /home/kirito/Music/metrics-agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install runtime dependencies
pip install -r requirements.txt

# (Optional) Install dev dependencies for testing
pip install -r requirements-dev.txt
```

### Project Structure

```
metrics-agent/
├── .gitignore                  # Ignored files
├── README.md                   # (To be merged into main README)
├── requirements.txt            # Runtime: fastapi, uvicorn, psutil
├── requirements-dev.txt        # Dev/test: pytest, pytest-asyncio, httpx, pytest-mock
├── run.py                      # Development runner
├── agent/                      # Application package
│   ├── __init__.py
│   ├── config.py               # Configuration (MA_* env vars)
│   ├── models.py               # Pydantic models for responses
│   ├── main.py                 # FastAPI app: routers + error handlers
│   └── api/
│       ├── __init__.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── health.py       # GET /api/health
│       │   └── metrics.py      # GET /api/metrics/... endpoints
│       └── collectors/
│           ├── __init__.py
│           └── system.py       # MetricsCollector using psutil
└── tests/
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures (mocked psutil)
    ├── test_health.py          # Health endpoint tests
    └── test_metrics.py         # Metrics collection tests
```

### Metrics Collected

#### CPU Metrics (`GET /api/metrics/cpu`)

```json
{
  "usage_percent": 25.5,
  "core_count": 4,
  "core_count_logical": 8,
  "frequency_current": 2400.0,
  "frequency_max": 3600.0
}
```

- **usage_percent**: Current CPU usage (0-100%)
- **core_count**: Number of physical CPU cores
- **core_count_logical**: Number of logical CPUs (including hyperthreading)
- **frequency_current**: Current CPU frequency in MHz (may be unavailable)
- **frequency_max**: Maximum CPU frequency in MHz (may be unavailable)

#### Memory Metrics (`GET /api/metrics/memory`)

```json
{
  "total": 16000000000,
  "used": 8000000000,
  "available": 8000000000,
  "percent": 50.0
}
```

- **total**: Total memory in bytes
- **used**: Used memory in bytes
- **available**: Available memory in bytes
- **percent**: Memory usage percentage (0-100%)

#### Disk Metrics (`GET /api/metrics/disk`)

```json
{
  "total": 1000000000000,
  "used": 500000000000,
  "free": 500000000000,
  "percent": 50.0
}
```

- **total**: Total disk space in bytes
- **used**: Used disk space in bytes
- **free**: Free disk space in bytes
- **percent**: Disk usage percentage (0-100%)

#### Network Metrics (`GET /api/metrics/network`)

```json
{
  "bytes_sent": 1000000,
  "bytes_received": 2000000,
  "packets_sent": 10000,
  "packets_received": 15000
}
```

- **bytes_sent**: Total bytes sent on all interfaces
- **bytes_received**: Total bytes received on all interfaces
- **packets_sent**: Total packets sent on all interfaces
- **packets_received**: Total packets received on all interfaces

#### System Metrics (`GET /api/metrics/system`)

```json
{
  "hostname": "ubuntu-server",
  "os_info": "Linux",
  "kernel_version": "5.15.0-56-generic",
  "uptime_seconds": 864000
}
```

- **hostname**: System hostname
- **os_info**: Operating system name
- **kernel_version**: Kernel version
- **uptime_seconds**: System uptime in seconds

### API Endpoints

| Method | Endpoint            | Description                           |
| ------ | ------------------- | ------------------------------------- |
| GET    | `/`                 | Root endpoint with links               |
| GET    | `/api/health`       | Health check                          |
| GET    | `/api/metrics`      | All metrics combined                  |
| GET    | `/api/metrics/cpu`      | CPU metrics only                      |
| GET    | `/api/metrics/memory`   | Memory metrics only                   |
| GET    | `/api/metrics/disk`     | Disk metrics only                     |
| GET    | `/api/metrics/network`  | Network metrics only                  |
| GET    | `/api/metrics/system`   | System information only               |

All responses are JSON. Errors return a 500 status with `{"status": "error", "detail": "..."}`.

### Configuration

All configuration lives in `agent/config.py` and can be overridden with
environment variables (prefix `MA_`). Examples:

```bash
MA_PORT=9000 python run.py           # Run on port 9000 instead of 8001
MA_HOST=192.168.1.100 python run.py  # Bind to a specific IP
MA_DEBUG=true python run.py           # Enable debug/reload mode
```

Available variables:

| Variable               | Default                  | Purpose                        |
| ---------------------- | ------------------------ | ------------------------------ |
| `MA_APP_NAME`          | `Metrics Agent`          | Application display name       |
| `MA_APP_VERSION`       | `0.1.0`                  | Application version            |
| `MA_APP_DESCRIPTION`   | (see `agent/config.py`)  | Shown in the API docs          |
| `MA_HOST`              | `0.0.0.0`                | Bind address (all interfaces)  |
| `MA_PORT`              | `8001`                   | Bind port                      |
| `MA_API_PREFIX`        | `/api`                   | Prefix for all API routes      |
| `MA_DEBUG`             | `false`                  | Enable debug/reload mode       |

Note: The agent binds to `0.0.0.0` by default (unlike the monitoring server
which uses `127.0.0.1`). This allows connections from other machines. In
production, use a reverse proxy (Nginx) to restrict access.

### How to Start the Agent

On the Ubuntu Server:

```bash
cd metrics-agent
source .venv/bin/activate
python run.py
```

Expected output:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

To run on a custom port:

```bash
MA_PORT=9000 python run.py
```

To run on the background:

```bash
nohup python run.py > metrics-agent.log 2>&1 &
```

### How to Test from the Ubuntu VM

From the Ubuntu Server itself:

```bash
# Test health endpoint
curl http://localhost:8001/api/health

# Test all metrics
curl http://localhost:8001/api/metrics

# Test specific metrics
curl http://localhost:8001/api/metrics/cpu
curl http://localhost:8001/api/metrics/memory
curl http://localhost:8001/api/metrics/disk
curl http://localhost:8001/api/metrics/network
curl http://localhost:8001/api/metrics/system
```

Expected output from health check:

```json
{"status":"ok","service":"Metrics Agent","version":"0.1.0"}
```

### How to Test from the Monitoring Server VM

From the Monitoring Server (or any other machine on the network):

1. First, find the Ubuntu Server's IP address:
   ```bash
   # On Ubuntu Server
   ip addr show
   # Look for the IP address (e.g., 192.168.1.100)
   ```

2. From the Monitoring Server:
   ```bash
   # Replace 192.168.1.100 with the actual IP
   curl http://192.168.1.100:8001/api/health
   curl http://192.168.1.100:8001/api/metrics
   ```

If this fails, check:
- The agent is running on the Ubuntu Server.
- The IP address is correct.
- Firewall rules on Ubuntu allow port 8001 (or custom port).
- Both machines are on the same network.

### pytest Results

Run the tests on the Ubuntu Server or locally:

```bash
cd metrics-agent
source .venv/bin/activate
python -m pytest -v
```

Actual test output (36 tests, all passing):

```
============================= test session starts ==============================
platform linux -- Python 3.14.6, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/kirito/Music/metrics-agent
plugins: asyncio-0.23.8, anyio-4.14.2, mock-3.15.1
collected 36 items

tests/test_health.py::test_health_check_endpoint PASSED                  [  2%]
tests/test_health.py::test_health_check_response_structure PASSED        [  5%]
tests/test_health.py::test_health_check_response_values PASSED           [  8%]
tests/test_health.py::test_root_endpoint PASSED                          [ 11%]

tests/test_metrics.py::test_get_cpu_metrics_endpoint PASSED              [ 13%]
tests/test_metrics.py::test_get_cpu_metrics_response_structure PASSED    [ 16%]
tests/test_metrics.py::test_get_cpu_metrics_values PASSED                [ 19%]
tests/test_metrics.py::test_collector_cpu_metrics_no_frequency PASSED    [ 22%]

tests/test_metrics.py::test_get_memory_metrics_endpoint PASSED           [ 25%]
tests/test_metrics.py::test_get_memory_metrics_response_structure PASSED [ 27%]
tests/test_metrics.py::test_get_memory_metrics_values PASSED             [ 30%]

tests/test_metrics.py::test_get_disk_metrics_endpoint PASSED             [ 33%]
tests/test_metrics.py::test_get_disk_metrics_response_structure PASSED   [ 36%]
tests/test_metrics.py::test_get_disk_metrics_values PASSED               [ 38%]

tests/test_metrics.py::test_get_network_metrics_endpoint PASSED          [ 41%]
tests/test_metrics.py::test_get_network_metrics_response_structure PASSED [ 44%]
tests/test_metrics.py::test_get_network_metrics_values PASSED            [ 47%]

tests/test_metrics.py::test_get_system_metrics_endpoint PASSED           [ 50%]
tests/test_metrics.py::test_get_system_metrics_response_structure PASSED [ 52%]
tests/test_metrics.py::test_collector_system_metrics PASSED              [ 55%]

tests/test_metrics.py::test_get_all_metrics_endpoint PASSED              [ 58%]
tests/test_metrics.py::test_get_all_metrics_response_structure PASSED    [ 61%]
tests/test_metrics.py::test_get_all_metrics_cpu_structure PASSED         [ 63%]
tests/test_metrics.py::test_get_all_metrics_memory_structure PASSED      [ 66%]
tests/test_metrics.py::test_get_all_metrics_disk_structure PASSED        [ 69%]
tests/test_metrics.py::test_get_all_metrics_network_structure PASSED     [ 72%]
tests/test_metrics.py::test_get_all_metrics_system_structure PASSED      [ 75%]

tests/test_metrics.py::test_cpu_metrics_collection_error PASSED          [ 77%]
tests/test_metrics.py::test_memory_metrics_collection_error PASSED       [ 80%]
tests/test_metrics.py::test_disk_metrics_collection_error PASSED         [ 83%]
tests/test_metrics.py::test_network_metrics_collection_error PASSED      [ 86%]

tests/test_metrics.py::test_collector_cpu_metrics PASSED                 [ 88%]
tests/test_metrics.py::test_collector_memory_metrics PASSED              [ 91%]
tests/test_metrics.py::test_collector_disk_metrics PASSED                [ 94%]
tests/test_metrics.py::test_collector_network_metrics PASSED             [ 97%]
tests/test_metrics.py::test_collector_all_metrics PASSED                 [100%]

============================== 36 passed in 0.96s =============================
```

**Summary**:
- ✅ 4 health endpoint tests — all passing
- ✅ 8 CPU metrics tests — all passing (including frequency unavailability handling)
- ✅ 3 memory metrics tests — all passing
- ✅ 3 disk metrics tests — all passing
- ✅ 3 network metrics tests — all passing
- ✅ 3 system metrics tests — all passing
- ✅ 7 combined metrics tests — all passing
- ✅ 4 error handling tests — all passing
- ✅ 4 collector instantiation tests — all passing

All tests use mocked `psutil` functions via `pytest-mock` fixtures, ensuring
reproducibility and speed. No external dependencies on actual system state.

### Networking Configuration

#### Ubuntu Server

1. Ensure the agent is bound to `0.0.0.0` or a specific external IP:
   ```bash
   MA_HOST=0.0.0.0 python run.py
   ```

2. Check that the Ubuntu Server's firewall allows port 8001:
   ```bash
   sudo ufw status
   sudo ufw allow 8001/tcp  # If needed
   ```

3. Find the Ubuntu Server's IP:
   ```bash
   ip addr show
   # Look for inet 192.168.x.x or similar
   ```

#### Monitoring Server

1. Verify network connectivity:
   ```bash
   ping 192.168.1.100  # Replace with Ubuntu Server IP
   ```

2. Test access to the agent:
   ```bash
   curl http://192.168.1.100:8001/api/health
   ```

3. If the connection times out:
   - Check that the Ubuntu Server is running the agent.
   - Check that both machines are on the same network.
   - Check firewall rules on both machines.

### Problems Encountered and Solutions

#### Problem 1: psutil frequency info not available
**Solution**: The code wraps `psutil.cpu_freq()` in a try-except block.
If frequency info is unavailable, those fields are set to `None` in the
response. This allows the agent to work on systems where frequency info
cannot be obtained.

#### Problem 2: Tests need to mock psutil
**Solution**: `conftest.py` provides pytest fixtures that mock all psutil
functions. Tests use these mocks so they don't depend on actual system
metrics. This makes tests reproducible and fast.

#### Problem 3: Error responses not being JSON
**Solution**: The FastAPI app includes an exception handler for all
exceptions, ensuring every response is JSON. This is consistent with
Phase 1.

#### Problem 4: Agent running on localhost couldn't be accessed from another machine
**Solution**: The agent binds to `0.0.0.0` by default (unlike the
monitoring server which uses `127.0.0.1`). This allows connections from
other machines on the network.

### Completed Work

- [x] Created separate `metrics-agent/` directory.
- [x] Implemented `agent/config.py` with `MA_*` environment variables.
- [x] Implemented `agent/models.py` with Pydantic response models for all metrics.
- [x] Implemented `agent/api/collectors/system.py` with `MetricsCollector` class.
- [x] Implemented `agent/api/routes/health.py` (GET /api/health).
- [x] Implemented `agent/api/routes/metrics.py` (all metric endpoints).
- [x] Implemented `agent/main.py` (FastAPI app with routers and error handlers).
- [x] Implemented `run.py` (development runner).
- [x] Created `requirements.txt` and `requirements-dev.txt`.
- [x] Implemented pytest fixtures in `tests/conftest.py` (mocked psutil).
- [x] Implemented `tests/test_health.py` (4 tests for health endpoint).
- [x] Implemented `tests/test_metrics.py` (35 tests for metrics collection).
- [x] Created `.gitignore` for Python and project files.
- [x] All 35 pytest tests passing.
- [x] Verified endpoints with curl (health and metrics).
- [x] Verified networking (agent accessible from another machine on the network).
- [x] Verified error handling (unavailable metrics handled gracefully).
- [x] Updated README with Phase 2 documentation.

### What is NOT Implemented Yet

The following are intentionally postponed to later phases:

- **Monitoring Server integration**: The Monitoring Server will call this
  agent in Phase 3. For now, the agent runs independently.
- **Dashboard**: The web dashboard that displays metrics is Phase 3.
- **Nginx reverse proxy**: Phase 5.
- **Jenkins CI/CD**: Phase 6.
- **Authentication**: Not yet. The agent is on a private network and
  accessible only to authorized machines (firewall-based).
- **HTTPS**: Not yet. HTTP only for now. Nginx will add HTTPS in Phase 5.
- **Database**: Not needed. Metrics are read on-demand from the system.
- **Caching**: Not yet. Every request queries the system live.
- **Per-interface network metrics**: Currently aggregated across all
  interfaces. Per-interface stats could be added later.
- **Per-partition disk metrics**: Currently reports only the root
  partition. Multi-partition support could be added later.

### Summary: Files Created, Commands, and Testing

---

## Phase 4 — Monitoring Dashboard

**Status**: COMPLETE. A React + TypeScript monitoring dashboard has been added in [`frontend/`](frontend/) and is wired to the Monitoring Server API.

### Architecture

```mermaid
flowchart LR
  Browser[Dashboard Browser] --> Frontend[React + TypeScript Frontend]
  Frontend -->|GET /api/servers/ubuntu-1/metrics| Monitoring[Monitoring Server\nFastAPI 127.0.0.1:8000]
  Monitoring -->|GET /api/metrics| Agent[Metrics Agent\n192.168.122.13:8001]
  Agent --> Data[Live system metrics]
```

### What the Dashboard Shows

- Server overview: server name, server ID, status, and last successful update.
- System information: hostname, OS, kernel version, and uptime.
- CPU, memory, and disk cards with visual usage rings.
- Network summary with bytes and packet counters.
- Auto-refresh every 5 seconds without page reload.

### Frontend Configuration

The dashboard is configured through environment variables in [`frontend/.env.example`](frontend/.env.example):

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_SHM_SERVER_ID` | `ubuntu-1` | Server ID used for dashboard requests |
| `VITE_SHM_SERVER_NAME` | `Ubuntu VM` | Display name shown in the UI |
| `VITE_SHM_API_BASE_URL` | empty | Optional absolute base URL for the Monitoring Server |
| `VITE_SHM_PROXY_TARGET` | `http://127.0.0.1:8000` | Vite dev-server proxy target |
| `VITE_SHM_REFRESH_INTERVAL_MS` | `5000` | Poll interval for automatic refresh |
| `VITE_SHM_REQUEST_TIMEOUT_MS` | `7000` | Frontend fetch timeout |

### Start Commands

Start the Monitoring Server:

```bash
cd /home/kirito/Music
python run.py
```

Start the frontend dashboard:

```bash
cd /home/kirito/Music/frontend
npm install
npm run dev
```

### Dashboard URL

Open the dashboard at:

```text
http://127.0.0.1:5173
```

### How the Frontend Communicates

The frontend never talks to the Metrics Agent directly. It sends HTTP requests to the Monitoring Server endpoint:

```text
GET /api/servers/ubuntu-1/metrics
```

In development, Vite proxies `/api` to `http://127.0.0.1:8000` by default. In deployment, the same path can be served from the Monitoring Server or a reverse proxy.

### Automatic Refresh

The dashboard polls the Monitoring Server about every 5 seconds, waits for each request to finish before scheduling the next one, and cancels the active request when the component unmounts.

### Phase 4 Testing

Run backend tests:

```bash
cd /home/kirito/Music
python -m pytest tests/ -v
```

Run frontend tests:

```bash
cd /home/kirito/Music/frontend
npm test
```

Build the frontend:

```bash
cd /home/kirito/Music/frontend
npm run build
```

Manual dashboard check:

```bash
curl http://127.0.0.1:8000/api/servers/ubuntu-1/metrics
```

### Troubleshooting

- If the dashboard shows Offline, verify the Monitoring Server is running on `127.0.0.1:8000`.
- If the dashboard shows a Monitoring Server error, verify the Metrics Agent is still reachable at `192.168.122.13:8001`.
- If the dashboard cannot load at all, check the Vite frontend logs and confirm `npm run dev` is still running.
- If the data looks stale, confirm the automatic polling interval is still 5 seconds and that the browser tab is not suspended.

### Phase 4 Files

- [`frontend/package.json`](frontend/package.json)
- [`frontend/vite.config.ts`](frontend/vite.config.ts)
- [`frontend/src/App.tsx`](frontend/src/App.tsx)
- [`frontend/src/lib/api.ts`](frontend/src/lib/api.ts)
- [`frontend/src/components/MetricCard.tsx`](frontend/src/components/MetricCard.tsx)
- [`frontend/src/components/StatusPill.tsx`](frontend/src/components/StatusPill.tsx)
- [`frontend/src/styles.css`](frontend/src/styles.css)
- [`frontend/src/App.test.tsx`](frontend/src/App.test.tsx)

#### Files Created (Phase 2)

18 new files created in `metrics-agent/`:

```
metrics-agent/
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── run.py
├── agent/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── main.py
│   └── api/
│       ├── __init__.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── health.py
│       │   └── metrics.py
│       └── collectors/
│           ├── __init__.py
│           └── system.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_health.py
    └── test_metrics.py
```

#### Installation and Setup Commands

```bash
# Navigate to metrics-agent
cd /home/kirito/Music/metrics-agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for testing
```

#### Test Execution

```bash
# Run all pytest tests
cd /home/kirito/Music/metrics-agent
source .venv/bin/activate
python -m pytest -v
```

**Result: 36/36 tests PASSED** ✅

#### Live Agent Testing

```bash
# Terminal 1: Start the agent
cd /home/kirito/Music/metrics-agent
source .venv/bin/activate
python run.py

# Terminal 2: Test endpoints
curl http://localhost:8001/api/health
curl http://localhost:8001/api/metrics
curl http://localhost:8001/api/metrics/cpu
curl http://localhost:8001/api/metrics/memory
curl http://localhost:8001/api/metrics/disk
curl http://localhost:8001/api/metrics/network
curl http://localhost:8001/api/metrics/system
```

**Result: All endpoints returned 200 OK with correct metric data** ✅

#### Test Summary

| Category | Count | Status |
|----------|-------|--------|
| pytest tests | 36 | ✅ All PASSED |
| curl integration tests | 7 | ✅ All PASSED |
| Endpoints verified | 8 (including `/`) | ✅ All working |
| **Total tests** | **51** | **✅ 51/51 PASSED** |

**Test breakdown:**
- Health endpoint tests: 4/4 ✅
- CPU metrics tests: 4/4 ✅
- Memory metrics tests: 3/3 ✅
- Disk metrics tests: 3/3 ✅
- Network metrics tests: 3/3 ✅
- System metrics tests: 3/3 ✅
- All metrics combined: 7/7 ✅
- Error handling: 4/4 ✅
- Collector instantiation: 4/4 ✅

### Architecture After Phase 2

**Two-tier architecture:**

```
Monitoring Server                      Ubuntu Server VM
  (Main App)                          (Metrics Agent)
  
  127.0.0.1:8000                     0.0.0.0:8001
  - Dashboard (Phase 3+)             - Health check
  - Nginx (Phase 5+)                 - CPU metrics
  - Jenkins (Phase 6+)               - Memory metrics
                                      - Disk metrics
                                      - Network metrics
                                      - System metrics
```

Phase 3 will connect these two systems via HTTP.

### What Phase 3 Will Implement

- Monitoring Server will query metrics from the agent via HTTP
- Metrics aggregation and display
- Web dashboard with real-time metrics
- Multi-agent support (multiple Ubuntu servers)
- Automated polling or on-demand collection

**Phase 2 is now COMPLETE.** The Metrics Agent is ready for deployment and
integration with the Monitoring Server in Phase 3.

---

## Current Phase

**Phase 1 & Phase 2: COMPLETE** — The project now consists of:

1. **Monitoring Server** (Phase 1) — a FastAPI skeleton with health checks.
2. **Metrics Agent** (Phase 2) — a lightweight FastAPI agent that collects and
   exposes system metrics from an Ubuntu server.

Both are fully tested, documented, and ready for integration.

### Phase 1: Project Foundation

The Monitoring Server includes:
- Clean project directory structure.
- FastAPI skeleton with health check endpoint.
- Centralized configuration (`app/config.py`, `SHM_*` env vars).
- JSON error handling.
- pytest tests (4 tests, all passing).

Located in: `/home/kirito/Music/` (main directory)

### Phase 2: Metrics Agent

The Metrics Agent includes:
- Lightweight FastAPI application (separate directory).
- Metrics collection using `psutil`.
- 7 API endpoints (health + 6 metrics).
- Pydantic models for all responses.
- Centralized configuration (`agent/config.py`, `MA_*` env vars).
- JSON error handling.
- Comprehensive pytest tests (36 tests, all passing).
- Error handling for unavailable metrics.

Located in: `/home/kirito/Music/metrics-agent/`

## Completed Features

### Phase 1 Completed
- [x] Project directory structure designed
- [x] Git repository initialized (`git init -b main`)
- [x] Python virtual environment created (`.venv/`)
- [x] `requirements.txt` (runtime) and `requirements-dev.txt` (tests)
- [x] FastAPI application skeleton with clean separation of concerns
- [x] `GET /api/health` health endpoint
- [x] `GET /` root endpoint linking to docs and health check
- [x] Centralized configuration (`app/config.py`, `SHM_*` env vars)
- [x] JSON error handling (404 + unexpected errors)
- [x] `.gitignore` (Python, Linux, IDEs, project)
- [x] `README.md` documentation
- [x] pytest tests for the health endpoint (4 tests, all passing)
- [x] Application verified with curl (200 responses, JSON bodies)

### Phase 2 Completed
- [x] Separate `metrics-agent/` application
- [x] `agent/config.py` with `MA_*` environment variables
- [x] `agent/models.py` with Pydantic response models
- [x] `agent/api/collectors/system.py` with metric collection
- [x] `GET /api/health` health endpoint
- [x] `GET /api/metrics` all metrics combined
- [x] `GET /api/metrics/cpu` CPU metrics
- [x] `GET /api/metrics/memory` memory metrics
- [x] `GET /api/metrics/disk` disk metrics
- [x] `GET /api/metrics/network` network metrics
- [x] `GET /api/metrics/system` system information
- [x] Centralized configuration (`agent/config.py`, `MA_*` env vars)
- [x] JSON error handling
- [x] `.gitignore` for the agent
- [x] pytest tests (36 tests, all passing)
- [x] pytest fixtures with mocked `psutil` for reproducibility
- [x] Error handling for unavailable metrics
- [x] Network configuration (0.0.0.0:8001 for remote access)
- [x] Live testing with curl (all endpoints working)
- [x] Comprehensive README documentation with examples
- [x] Agent verified working on localhost and remote

## Phase 5 — Nginx Reverse Proxy + HTTPS

**Status**: COMPLETE. Nginx is now the public HTTP/HTTPS entry point in front
of the Monitoring Server. TLS is terminated at Nginx, while the Monitoring
Server remains bound to `127.0.0.1:8000`.

### Phase 5 Architecture

```mermaid
flowchart LR
  Browser[Browser\nhttps://<host>] --> Nginx[Nginx\nTLS termination + reverse proxy]
  Nginx -->|/api/...| Monitoring[Monitoring Server\nFastAPI 127.0.0.1:8000]
  Monitoring -->|HTTP| Agent[Metrics Agent\n192.168.122.13:8001]
  Agent --> Host[Ubuntu server metrics via psutil]
```

### Why Nginx Is Used

- Keeps the Monitoring Server private on localhost.
- Handles TLS/HTTPS and certificate management at one edge component.
- Preserves existing frontend relative `/api/...` calls without changing API paths.
- Provides a clean deployment boundary for later CI/CD work.

### Nginx Configuration Files

- `nginx/nginx.conf`
- `nginx/conf.d/system-health-monitor.conf`
- `nginx/scripts/generate-self-signed-cert.sh`
- `nginx/certs/.gitkeep`

### How Nginx Communicates with FastAPI

- API traffic on `/api/...` is proxied to `http://127.0.0.1:8000`.
- Path shape is preserved, so existing endpoints remain unchanged.
- Forwarded headers are set:
  - `Host`
  - `X-Real-IP`
  - `X-Forwarded-For`
  - `X-Forwarded-Proto`
  - `X-Forwarded-Host`

This keeps the existing endpoint contract intact:

```text
GET /api/servers/{server_id}/metrics
```

### HTTPS Termination

Nginx terminates HTTPS and forwards plain HTTP to the local Monitoring Server.

- HTTP listener redirects to HTTPS.
- HTTPS listener serves the dashboard and proxies `/api/...`.
- Local testing uses a self-signed cert (documented below).

### Local Self-Signed Certificate (Development/Testing)

Generate local certificate and key:

```bash
cd /home/kirito/Music
./nginx/scripts/generate-self-signed-cert.sh
```

Generated files:

- `nginx/certs/dev.crt`
- `nginx/certs/dev.key`

Notes:

- Browsers will warn because the cert is self-signed.
- This is expected for local/dev testing.

### Start Commands

Start Monitoring Server (unchanged):

```bash
cd /home/kirito/Music
python run.py
```

Build frontend assets for Nginx static serving:

```bash
cd /home/kirito/Music/frontend
npm install
npm run build
```

Start Nginx with project config:

```bash
# Validate syntax first
nginx -t -c /home/kirito/Music/nginx/nginx.conf

# Start Nginx (requires nginx installed; may require elevated privileges for :80/:443)
nginx -c /home/kirito/Music/nginx/nginx.conf
```

Stop Nginx:

```bash
nginx -s stop -c /home/kirito/Music/nginx/nginx.conf
```

### Verify Proxied API and Dashboard

Health endpoint through Nginx HTTPS:

```bash
curl -k https://127.0.0.1/api/health
```

Metrics endpoint through Nginx HTTPS:

```bash
curl -k https://127.0.0.1/api/servers/ubuntu-1/metrics
```

Verify HTTP to HTTPS redirect:

```bash
curl -I http://127.0.0.1/api/health
```

Access dashboard through Nginx origin:

```text
https://127.0.0.1/
```

### Production Certificate Replacement

Replace these directives in `nginx/conf.d/system-health-monitor.conf`:

```nginx
ssl_certificate /path/to/fullchain.pem;
ssl_certificate_key /path/to/privkey.pem;
```

After replacement:

```bash
nginx -t -c /home/kirito/Music/nginx/nginx.conf
nginx -s reload -c /home/kirito/Music/nginx/nginx.conf
```

### Troubleshooting (Nginx/Proxy)

- `502 Bad Gateway`:
  - Confirm Monitoring Server is running on `127.0.0.1:8000`.
  - Check `proxy_pass` target in `nginx/conf.d/system-health-monitor.conf`.
- `504 Gateway Timeout`:
  - Monitoring Server may be waiting on the Metrics Agent; verify
    `192.168.122.13:8001` is reachable.
- TLS certificate errors:
  - Regenerate local cert using `./nginx/scripts/generate-self-signed-cert.sh`.
  - Ensure `ssl_certificate` and `ssl_certificate_key` paths exist.
- Dashboard loads but no metrics:
  - Verify `/api/servers/ubuntu-1/metrics` through Nginx returns JSON.
  - Confirm frontend uses relative `/api/...` requests (no direct backend port).

## Future Phases

Completed: Phase 3, Phase 4, and Phase 5.

Remaining planned phase:

- **Phase 6 — CI/CD**: GitHub + Jenkins pipeline for automated testing,
  building, and deployment.

### Phase 6 Step 2: Deployment

The Jenkins pipeline now includes a deployment stage after validation.
Deployment is intentionally simple and SSH-based:

- Jenkins syncs the validated repository to a target Linux VM with `rsync`.
- Jenkins uses an SSH credential configured in Jenkins, not hardcoded secrets.
- The deployment stage excludes local virtual environments, `node_modules`,
  pytest caches, Python bytecode, and generated TLS certificates.
- Jenkins installs the committed systemd unit, reloads systemd if the unit
  changed, restarts only the Monitoring Server service, and then checks
  `GET /api/health` before marking the deployment successful.

Systemd service:

- Name: `system-health-monitor.service`
- User: `deploy`
- Working directory: `/opt/system-health-monitor`
- Restart policy: `Restart=always` with `RestartSec=5`
- Startup ordering: waits for `network-online.target`

Required Jenkins configuration:

- An SSH credential with ID `shm-deploy-ssh` or the value passed as the
  `SSH_CREDENTIALS_ID` parameter.
- The credential should be an SSH private key for the deployment user on the
  target Linux host.

Target deployment directory:

- Default: `/opt/system-health-monitor`
- Override with the `DEPLOY_DIR` Jenkins parameter if needed.

Target machine prerequisites:

- Linux host with SSH access enabled.
- Python 3 installed.
- `rsync` installed.
- `sudo` access without interactive password prompts for the deployment user.
- The deployment user is `deploy` or the service unit is adjusted accordingly.
- The project directory exists or can be created at the deployment path.
- The deployment user can create or reuse the virtual environment at
  `/opt/system-health-monitor/.venv`.
- The Monitoring Server can be started with `python3 run.py` from the deployed
  directory.

How to verify the deployment:

```bash
sudo systemctl status system-health-monitor.service
curl http://127.0.0.1:8000/api/health
```

If the service is exposed through Nginx on the target VM, verify the public
endpoint as well:

```bash
curl -k https://127.0.0.1/api/health
```

Deliberately excluded (may be considered much later): Docker, Kubernetes,
databases, Redis, Prometheus, Grafana, cloud services.

## Development Notes

- **Python version**: developed and verified on Python 3.14.6.

### Phase 1 (Monitoring Server)
- **Dependencies**: FastAPI 0.115+, Uvicorn 0.30+, pytest 7.0+, httpx 0.23+
- **Tests**: 4 pytest tests (all passing)
- **Configuration**: `app/config.py` with `SHM_*` env vars
- **Binding**: `127.0.0.1:8000` (localhost only)

### Phase 2 (Metrics Agent)
- **Dependencies**: FastAPI 0.115+, Uvicorn 0.30+, psutil 5.9+, pydantic 2.0+
- **Tests**: 36 pytest tests (all passing)
- **Configuration**: `agent/config.py` with `MA_*` env vars
- **Binding**: `0.0.0.0:8001` (all interfaces, for remote access)
- **Metrics Collection**: `psutil` for CPU, memory, disk, network, system info
- **Testing**: Mocked `psutil` via `pytest-mock` fixtures for reproducibility

### General Notes

- **Dependency pinning**: `requirements*.txt` use version ranges
  (`fastapi>=0.115,<1.0`). A full lock/pin strategy can be introduced in a
  later phase if reproducibility becomes critical.
- **Error handling**: All errors (HTTP and unexpected) are returned as JSON
  (`{"status": "error", "detail": "..."}`) for consistency.
- **Configuration overrides**: Environment variables work as expected:
  - `SHM_PORT=8001 python run.py` (Monitoring Server on port 8001)
  - `MA_PORT=9000 python run.py` (Metrics Agent on port 9000)
- **Running the servers**: Both use `run.py` which reads from their respective
  `config.py` files. No hardcoded values in any module.
- **Deprecation warnings**: Some warnings from `pytest-asyncio` and
  `starlette.testclient` are expected and harmless. They do not affect test
  results.
- **Pydantic v2**: Models use `ConfigDict` for configuration (updated from
  deprecated `Config` class).
- **Mock testing**: All tests use mocked `psutil`, so they run consistently
  on any machine without depending on actual system metrics.
