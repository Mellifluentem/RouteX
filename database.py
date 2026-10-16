
import os
import sqlite3
from pathlib import Path
from contextlib import closing

DATABASE_PATH = Path(
    os.environ.get(
        "ROUTEX_DATABASE_PATH",
        Path(__file__).resolve().parent / "routex.db",
    )
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS monitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                monitor_type TEXT NOT NULL
                    CHECK (monitor_type IN ('ping', 'http'))
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id INTEGER NOT NULL,
                status TEXT NOT NULL
                    CHECK (status IN ('UP', 'DOWN')),
                latency_ms REAL,
                error TEXT,
                checked_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                FOREIGN KEY (monitor_id)
                    REFERENCES monitors(id)
                    ON DELETE CASCADE
            )
            """
        )

        connection.commit()
