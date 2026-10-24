import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import backup_db


class TestBackupDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.database = self.root / "routex.db"
        self.backup = self.root / "backup.db"

        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "CREATE TABLE monitors (id INTEGER PRIMARY KEY, name TEXT)"
            )
            connection.execute(
                "INSERT INTO monitors (name) VALUES (?)", ("test-monitor",)
            )

    def test_backup_copies_database(self):
        with patch.object(backup_db, "DATABASE_PATH", self.database):
            backup_db.backup_database(self.backup)

        with sqlite3.connect(self.backup) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM monitors"
            ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_backup_rejects_same_source_and_destination(self):
        with patch.object(backup_db, "DATABASE_PATH", self.database):
            with self.assertRaises(ValueError):
                backup_db.backup_database(self.database)

    def test_verify_rejects_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            backup_db.verify_database(self.root / "missing.db")

    def test_verify_rejects_invalid_database(self):
        invalid = self.root / "invalid.db"
        invalid.write_text("not a SQLite database")

        with self.assertRaises(sqlite3.DatabaseError):
            backup_db.verify_database(invalid)

    def test_restore_copies_backup_and_keeps_safety_backup(self):
        with sqlite3.connect(self.backup) as connection:
            connection.execute(
                "CREATE TABLE monitors (id INTEGER PRIMARY KEY, name TEXT)"
            )
            connection.execute(
                "INSERT INTO monitors (name) VALUES (?)", ("restored-monitor",)
            )

        with patch.object(backup_db, "DATABASE_PATH", self.database):
            backup_db.restore_database(self.backup)

        with sqlite3.connect(self.database) as connection:
            name = connection.execute(
                "SELECT name FROM monitors"
            ).fetchone()[0]

        self.assertEqual(name, "restored-monitor")
        safety_backups = list(self.root.glob("routex_before_restore_*.db"))
        self.assertEqual(len(safety_backups), 1)

    def test_restore_rejects_same_source_and_destination(self):
        with patch.object(backup_db, "DATABASE_PATH", self.database):
            with self.assertRaises(ValueError):
                backup_db.restore_database(self.database)


if __name__ == "__main__":
    unittest.main()
