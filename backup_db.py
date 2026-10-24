import argparse
import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

from database import DATABASE_PATH


def verify_database(path: Path) -> None:
    path = path.resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Database file not found: {path}")

    with sqlite3.connect(path) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]

    if result != "ok":
        raise RuntimeError(f"Database integrity check failed: {result}")

    print(f"Integrity: ok ({path})")


def backup_database(destination: Path) -> None:
    source_path = Path(DATABASE_PATH).resolve()
    destination = destination.resolve()

    if not source_path.is_file():
        raise FileNotFoundError(f"Database not found: {source_path}")
    if source_path == destination:
        raise ValueError("Backup destination must differ from the source database.")

    destination.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(source_path) as source:
        with sqlite3.connect(destination) as backup:
            source.backup(backup)

    verify_database(destination)
    print(f"Backup created: {destination}")


def restore_database(source: Path) -> None:
    source = source.resolve()
    destination = Path(DATABASE_PATH).resolve()

    if source == destination:
        raise ValueError("Restore source must differ from the active database.")

    verify_database(source)

    if not destination.is_file():
        raise FileNotFoundError(f"Active database not found: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety_backup = destination.with_name(
        f"{destination.stem}_before_restore_{timestamp}{destination.suffix}"
    )

    with sqlite3.connect(destination) as current:
        with sqlite3.connect(safety_backup) as backup:
            current.backup(backup)

    verify_database(safety_backup)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix="routex_restore_",
            suffix=".db",
            dir=destination.parent,
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

        with sqlite3.connect(source) as source_db:
            with sqlite3.connect(temp_path) as temp_db:
                source_db.backup(temp_db)

        verify_database(temp_path)
        os.replace(temp_path, destination)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    verify_database(destination)
    print(f"Restore completed: {destination}")
    print(f"Safety backup kept: {safety_backup}")


def main() -> None:
    parser = argparse.ArgumentParser(description="RouteX database backup utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup", help="Create a database backup")
    backup_parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        help="Backup file path (defaults to a timestamped file)",
    )

    verify_parser = subparsers.add_parser("verify", help="Verify a database file")
    verify_parser.add_argument("path", type=Path)

    restore_parser = subparsers.add_parser("restore", help="Restore a database backup")
    restore_parser.add_argument("source", type=Path, help="Backup file to restore")

    args = parser.parse_args()

    if args.command == "backup":
        destination = args.destination
        if destination is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = Path(DATABASE_PATH).with_name(
                f"routex_backup_{timestamp}.db"
            )
        backup_database(destination)
    elif args.command == "verify":
        verify_database(args.path)
    elif args.command == "restore":
        restore_database(args.source)


if __name__ == "__main__":
    main()
