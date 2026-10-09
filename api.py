
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(
    title="routeX API",
    description="A self-hosted monitoring platform",
    version="0.3.0",
)

# Temporary in-memory storage
monitors = []
next_monitor_id = 1


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target: str = Field(min_length=1, max_length=500)
    monitor_type: Literal["ping", "http"]


@app.get("/")
def root():
    return {
        "project": "routeX",
        "version": "0.3.0",
        "message": "Monitoring API is running",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/monitors")
def list_monitors():
    return {"monitors": monitors}


@app.post("/monitors", status_code=201)
def create_monitor(monitor: MonitorCreate):
    global next_monitor_id

    new_monitor = {
        "id": next_monitor_id,
        "name": monitor.name.strip(),
        "target": monitor.target.strip(),
        "monitor_type": monitor.monitor_type,
    }

    if not new_monitor["name"] or not new_monitor["target"]:
        raise HTTPException(
            status_code=422,
            detail="Name and target cannot contain only whitespace",
        )

    monitors.append(new_monitor)
    next_monitor_id += 1

    return new_monitor

@app.get("/monitors/{monitor_id}")
def get_monitor(monitor_id: int):
    for monitor in monitors:
        if monitor["id"] == monitor_id:
            return monitor

    raise HTTPException(
        status_code=404,
        detail="Monitor not found",
    )


@app.delete("/monitors/{monitor_id}")
def delete_monitor(monitor_id: int):
    for index, monitor in enumerate(monitors):
        if monitor["id"] == monitor_id:
            deleted_monitor = monitors.pop(index)
            return {
                "message": "Monitor deleted successfully",
                "monitor": deleted_monitor,
            }

    raise HTTPException(
        status_code=404,
        detail="Monitor not found",
    )


