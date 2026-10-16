
from contextlib import closing
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from database import get_connection, init_db
from checks.ping import check_ping
from checks.http import check_http


app = FastAPI(
    title="routeX API",
    description="A self-hosted monitoring platform",
    version="0.4.0",
)

# Veritabanı ve tablo yoksa oluştur.
init_db()


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target: str = Field(min_length=1, max_length=500)
    monitor_type: Literal["ping", "http"]


@app.get("/")
def root():
    return {
        "project": "routeX",
        "version": "0.4.0",
        "message": "Monitoring API is running",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/monitors")
def list_monitors():
    with closing(get_connection()) as connection:
        rows = connection.execute(
            "SELECT id, name, target, monitor_type FROM monitors ORDER BY id"
        ).fetchall()

    return {"monitors": [dict(row) for row in rows]}


@app.post("/monitors", status_code=201)
def create_monitor(monitor: MonitorCreate):
    name = monitor.name.strip()
    target = monitor.target.strip()

    if not name or not target:
        raise HTTPException(
            status_code=422,
            detail="Name and target cannot contain only whitespace",
        )

    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO monitors (name, target, monitor_type)
            VALUES (?, ?, ?)
            """,
            (name, target, monitor.monitor_type),
        )
        connection.commit()

        row = connection.execute(
            "SELECT id, name, target, monitor_type FROM monitors WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return dict(row)


@app.get("/monitors/{monitor_id}")
def get_monitor(monitor_id: int):
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT id, name, target, monitor_type
            FROM monitors WHERE id = ?
            """,
            (monitor_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Monitor not found")

    return dict(row)


@app.delete("/monitors/{monitor_id}")
def delete_monitor(monitor_id: int):
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT id, name, target, monitor_type
            FROM monitors WHERE id = ?
            """,
            (monitor_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        connection.execute(
            "DELETE FROM monitors WHERE id = ?",
            (monitor_id,),
        )
        connection.commit()

    return {
        "message": "Monitor deleted successfully",
        "monitor": dict(row),
    }


@app.post("/monitors/{monitor_id}/check")
def run_monitor_check(monitor_id: int):
    monitor = get_monitor(monitor_id)

    if monitor["monitor_type"] == "ping":
        result = check_ping(monitor["target"])
    else:
        result = check_http(monitor["target"])

    return {
        "monitor": monitor,
        "check": result,
    }
