from unittest.mock import patch

import unittest

from fastapi.testclient import TestClient

import api


class TestMonitorAPI(unittest.TestCase):

    def setUp(self):
        # Her test temiz bir bellek içi listeyle başlasın.
        api.monitors.clear()
        api.next_monitor_id = 1
        self.client = TestClient(api.app)

    def test_root_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project"], "routeX")

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_create_monitor(self):
        response = self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], 1)
        self.assertEqual(response.json()["name"], "Localhost")

    def test_list_monitors(self):
        self.client.post(
            "/monitors",
            json={
                "name": "Example Website",
                "target": "https://example.com",
                "monitor_type": "http",
            },
        )

        response = self.client.get("/monitors")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["monitors"]), 1)
        self.assertEqual(
            response.json()["monitors"][0]["monitor_type"],
            "http",
        )

    def test_get_monitor_by_id(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.get(f"/monitors/{monitor_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], monitor_id)

    def test_get_missing_monitor_returns_404(self):
        response = self.client.get("/monitors/999")

        self.assertEqual(response.status_code, 404)

    def test_delete_monitor(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.delete(f"/monitors/{monitor_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            "Monitor deleted successfully",
        )

        list_response = self.client.get("/monitors")
        self.assertEqual(list_response.json()["monitors"], [])

    def test_delete_missing_monitor_returns_404(self):
        response = self.client.delete("/monitors/999")

        self.assertEqual(response.status_code, 404)

    def test_invalid_monitor_type_returns_422(self):
        response = self.client.post(
            "/monitors",
            json={
                "name": "Example",
                "target": "example.com",
                "monitor_type": "ftp",
            },
        )

        self.assertEqual(response.status_code, 422)

    @patch("api.check_ping")
    def test_run_ping_check(self, mock_check_ping):
        mock_check_ping.return_value = {
            "status": "UP",
            "latency_ms": 10.31,
            "error": None,
        }

        self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )

        response = self.client.post("/monitors/1/check")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["check"]["status"], "UP")
        mock_check_ping.assert_called_once_with("127.0.0.1")

    @patch("api.check_http")
    def test_run_http_check(self, mock_check_http):
        mock_check_http.return_value = {
            "status": "UP",
            "latency_ms": 25.5,
            "http_status_code": 200,
            "error": None,
        }

        self.client.post(
            "/monitors",
            json={
                "name": "Example Website",
                "target": "https://example.com",
                "monitor_type": "http",
            },
        )

        response = self.client.post("/monitors/1/check")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["check"]["status"], "UP")
        mock_check_http.assert_called_once_with("https://example.com")

    def test_run_check_for_missing_monitor_returns_404(self):
        response = self.client.post("/monitors/999/check")

        self.assertEqual(response.status_code, 404)



if __name__ == "__main__":
    unittest.main()
