from fastapi import FastAPI
import random

app = FastAPI(title="System Health Monitor")

# 1. Root endpoint - helpful for checking if the server is alive
@app.get("/")
def read_root():
    return {"status": "online", "message": "Health Monitor API is active"}

# 2. CPU Usage simulation
@app.get("/api/cpu")
def get_cpu():
    # We use random for now; in Phase 2 we will use real system data
    return {
        "metric": "CPU Usage",
        "value": random.randint(10, 95),
        "unit": "percentage"
    }

# 3. RAM Usage simulation
@app.get("/api/ram")
def get_ram():
    return {
        "metric": "Memory Usage",
        "value": round(random.uniform(2.0, 14.0), 1),
        "unit": "GB"
    }

# 4. Disk Usage simulation
@app.get("/api/disk")
def get_disk():
    return {
        "metric": "Disk Space Used",
        "value": 45.2,
        "unit": "percentage"
    }
