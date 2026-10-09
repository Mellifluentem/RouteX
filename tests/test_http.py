
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from checks.http import check_http


class TestHTTP(unittest.TestCase):

    @patch("checks.http.urllib.request.urlopen")
    def test_successful_request(self, mock_urlopen):
        response = MagicMock()
        response.status = 200
        mock_urlopen.return_value.__enter__.return_value = response

        result = check_http("https://example.com")

        self.assertEqual(result["status"], "UP")
        self.assertEqual(result["http_status_code"], 200)
        self.assertIsNotNone(result["latency_ms"])
        self.assertIsNone(result["error"])

    @patch("checks.http.urllib.request.urlopen")
    def test_http_404(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            "https://example.com/missing",
            404,
            "Not Found",
            {},
            None,
        )

        result = check_http("https://example.com/missing")

        self.assertEqual(result["status"], "DOWN")
        self.assertEqual(result["http_status_code"], 404)
        self.assertEqual(result["error"], "HTTP status 404")

    def test_invalid_url(self):
        result = check_http("ftp://example.com")

        self.assertEqual(result["status"], "DOWN")
        self.assertIsNone(result["http_status_code"])
        self.assertEqual(
            result["error"],
            "A valid HTTP or HTTPS URL is required",
        )

    def test_empty_url(self):
        result = check_http("")

        self.assertEqual(result["status"], "DOWN")
        self.assertEqual(result["error"], "URL cannot be empty")


if __name__ == "__main__":
    unittest.main()
