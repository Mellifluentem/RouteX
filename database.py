
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
        connection.execute("PRAGMA foreign_keys = OFF")

        try:
            connection.execute("BEGIN")

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS monitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    monitor_type TEXT NOT NULL
                        CHECK (monitor_type IN ('ping', 'http', 'tcp')),
                    enabled INTEGER NOT NULL DEFAULT 1,
                    port INTEGER
                )
                """
            )

            columns = connection.execute(
                "PRAGMA table_info(monitors)"
            ).fetchall()
            column_names = [column["name"] for column in columns]

            # Migrate older databases that do not have the enabled column.
            if "enabled" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE monitors
                    ADD COLUMN enabled INTEGER NOT NULL DEFAULT 1
                    """
                )

            # Migrate older databases that do not have the port column.
            if "port" not in column_names:
                connection.execute(
                    "ALTER TABLE monitors ADD COLUMN port INTEGER"
                )

            table_sql = connection.execute(
                """
                SELECT sql FROM sqlite_master
                WHERE type = 'table' AND name = 'monitors'
                """
            ).fetchone()["sql"]

            # Rebuild the table if its CHECK constraint does not allow TCP.
            if "'tcp'" not in table_sql:
                connection.execute(
                    """
                    CREATE TABLE monitors_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        target TEXT NOT NULL,
                        monitor_type TEXT NOT NULL
                            CHECK (monitor_type IN ('ping', 'http', 'tcp')),
                        enabled INTEGER NOT NULL DEFAULT 1,
                        port INTEGER
                    )
                    """
                )

                connection.execute(
                    """
                    INSERT INTO monitors_new
                        (id, name, target, monitor_type, enabled, port)
                    SELECT id, name, target, monitor_type, enabled, port
                    FROM monitors
                    """
                )

                connection.execute("DROP TABLE monitors")
                connection.execute(
                    "ALTER TABLE monitors_new RENAME TO monitors"
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

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.execute("PRAGMA foreign_keys = ON")
