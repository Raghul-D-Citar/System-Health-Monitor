import psutil
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="System Health Monitor")

app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/api/health")
def health_check():
    cpu_percent = psutil.cpu_percent(interval=0.5)

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_percent": cpu_percent,
        "memory": {
            "total": mem.total,
            "used": mem.used,
            "percent": mem.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "percent": disk.percent,
        },
    }
