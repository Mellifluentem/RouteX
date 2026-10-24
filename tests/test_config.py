import os
import subprocess
import sys
import unittest


class TestDatabaseConfiguration(unittest.TestCase):
    def test_database_path_from_environment(self):
        expected_path = "/tmp/routex_config_test.db"
        env = os.environ.copy()
        env["ROUTEX_DATABASE_PATH"] = expected_path

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from database import DATABASE_PATH; print(DATABASE_PATH)",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertEqual(result.stdout.strip(), expected_path)


if __name__ == "__main__":
    unittest.main()
