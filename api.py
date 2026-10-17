
import asyncio
from contextlib import asynccontextmanager, closing
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic import field_validator

from database import get_connection, init_db
from checks.ping import check_ping
from checks.http import check_http
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(automatic_monitoring())
    yield
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="routeX API",
    description="A self-hosted monitoring platform",
    version="0.6.0",
    lifespan=lifespan,
)


BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

init_db()

CHECK_INTERVAL_SECONDS = 60


async def automatic_monitoring():
    while True:
        try:
            with closing(get_connection()) as connection:
                monitors = connection.execute(
                    """
                    SELECT id, name, target, monitor_type
                    FROM monitors
                    WHERE enabled = 1
                    """
                ).fetchall()

            for monitor in monitors:
                monitor = dict(monitor)

                if monitor["monitor_type"] == "ping":
                    result = await asyncio.to_thread(
                        check_ping, monitor["target"]
                    )
                else:
                    result = await asyncio.to_thread(
                        check_http, monitor["target"]
                    )

                with closing(get_connection()) as connection:
                    connection.execute(
                        """
                        INSERT INTO checks
                            (monitor_id, status, latency_ms, error)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            monitor["id"],
                            result["status"],
                            result.get("latency_ms"),
                            result.get("error"),
                        ),
                    )
                    connection.commit()

        except Exception as error:
            print(f"Automatic monitoring error: {error}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)




class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    monitor_type: Literal["ping", "http"]
    target: str = Field(min_length=1, max_length=500)

    @field_validator("target")
    @classmethod
    def normalize_http_target(cls, target: str, info):
        target = target.strip()

        if info.data.get("monitor_type") == "http":
            if not target.startswith(("http://", "https://")):
                target = "https://" + target

        return target



@app.get("/")
def root():
    return FileResponse(BASE_DIR / "templates" / "index.html")


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




class MonitorEnabledUpdate(BaseModel):
    enabled: bool


@app.patch("/monitors/{monitor_id}/enabled")
def set_monitor_enabled(
    monitor_id: int,
    update: MonitorEnabledUpdate,
):
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT id FROM monitors WHERE id = ?",
            (monitor_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Monitor not found",
            )

        connection.execute(
            "UPDATE monitors SET enabled = ? WHERE id = ?",
            (int(update.enabled), monitor_id),
        )
        connection.commit()

        updated_row = connection.execute(
            """
            SELECT id, name, target, monitor_type, enabled
            FROM monitors
            WHERE id = ?
            """,
            (monitor_id,),
        ).fetchone()

    return {"monitor": dict(updated_row)}






@app.post("/monitors/{monitor_id}/check")
def run_monitor_check(monitor_id: int):
    monitor = get_monitor(monitor_id)

    if monitor["monitor_type"] == "ping":
        result = check_ping(monitor["target"])
    else:
        result = check_http(monitor["target"])

    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO checks (monitor_id, status, latency_ms, error)
            VALUES (?, ?, ?, ?)
            """,
            (
                monitor["id"],
                result["status"],
                result.get("latency_ms"),
                result.get("error"),
            ),
        )
        connection.commit()

    return {
        "monitor": monitor,
        "check": result,
    }


@app.get("/monitors/{monitor_id}/checks")
def get_monitor_checks(monitor_id: int):
    # Check that the monitor exists
    get_monitor(monitor_id)

    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT id, monitor_id, status, latency_ms, error, checked_at
            FROM checks
            WHERE monitor_id = ?
            ORDER BY id DESC
            """,
            (monitor_id,),
        ).fetchall()

    return {"checks": [dict(row) for row in rows]}
