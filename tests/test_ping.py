
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from checks.ping import check_ping


class TestPing(unittest.TestCase):

    @patch("checks.ping.subprocess.run")
    def test_successful_ping(self, mock_run):
        mock_run.return_value = SimpleNamespace(returncode=0)

        result = check_ping("127.0.0.1")

        self.assertEqual(result["status"], "UP")
        self.assertIsNotNone(result["latency_ms"])
        self.assertIsNone(result["error"])

    @patch("checks.ping.subprocess.run")
    def test_failed_ping(self, mock_run):
        mock_run.return_value = SimpleNamespace(returncode=1)

        result = check_ping("192.0.2.1")

        self.assertEqual(result["status"], "DOWN")
        self.assertIsNone(result["latency_ms"])
        self.assertIsNotNone(result["error"])

    def test_empty_target(self):
        result = check_ping("")

        self.assertEqual(result["status"], "DOWN")
        self.assertEqual(
            result["error"], "Target cannot be empty"
        )

    def test_invalid_timeout(self):
        result = check_ping("127.0.0.1", timeout_seconds=0)

        self.assertEqual(result["status"], "DOWN")
        self.assertEqual(
            result["error"], "Timeout must be at least 1 second"
        )


if __name__ == "__main__":
    unittest.main()
