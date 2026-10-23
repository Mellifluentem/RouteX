
import os
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient


import api


class TestMonitorAPI(unittest.TestCase):

    def setUp(self):
        self.test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.test_db.close()

        import database
        database.DATABASE_PATH = self.test_db.name
        api.DATABASE_PATH = self.test_db.name

        api.init_db()
        self.client = TestClient(api.app)


    def test_root_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("routeX", response.text)

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
        self.assertGreater(response.json()["id"], 0)
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


    def test_disable_monitor(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.patch(
            f"/monitors/{monitor_id}/enabled",
            json={"enabled": False},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["monitor"]["enabled"], 0)

    def test_enable_monitor(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        self.client.patch(
            f"/monitors/{monitor_id}/enabled",
            json={"enabled": False},
        )
        response = self.client.patch(
            f"/monitors/{monitor_id}/enabled",
            json={"enabled": True},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["monitor"]["enabled"], 1)

    def test_set_enabled_for_missing_monitor_returns_404(self):
        response = self.client.patch(
            "/monitors/999/enabled",
            json={"enabled": False},
        )

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


        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.post(f"/monitors/{monitor_id}/check")


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

        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Example Website",
                "target": "https://example.com",
                "monitor_type": "http",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.post(f"/monitors/{monitor_id}/check")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["check"]["status"], "UP")
        mock_check_http.assert_called_once_with("https://example.com")




    def test_create_docker_monitor(self):
        response = self.client.post(
            "/monitors",
            json={
                "name": "Docker Test",
                "target": "test-container",
                "monitor_type": "docker",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["monitor_type"], "docker")
        self.assertEqual(response.json()["target"], "test-container")

    @patch("api.check_container")
    def test_run_docker_check(self, mock_check_container):
        mock_check_container.return_value = {
            "status": "UP",
            "latency_ms": 3.5,
            "error": None,
        }

        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Docker Test",
                "target": "test-container",
                "monitor_type": "docker",
            },
        )
        self.assertEqual(create_response.status_code, 201)

        monitor_id = create_response.json()["id"]
        response = self.client.post(
            f"/monitors/{monitor_id}/check"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["check"]["status"], "UP")
        mock_check_container.assert_called_once_with("test-container")



    def test_run_check_for_missing_monitor_returns_404(self):
        response = self.client.post("/monitors/999/check")

        self.assertEqual(response.status_code, 404)


    @patch("api.check_ping")
    def test_run_check_is_saved_to_history(self, mock_check_ping):
        mock_check_ping.return_value = {
            "status": "UP",
            "latency_ms": 12.5,
            "error": None,
        }

        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        check_response = self.client.post(
            f"/monitors/{monitor_id}/check"
        )

        self.assertEqual(check_response.status_code, 200)

        history_response = self.client.get(
            f"/monitors/{monitor_id}/checks"
        )

        self.assertEqual(history_response.status_code, 200)
        checks = history_response.json()["checks"]
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]["monitor_id"], monitor_id)
        self.assertEqual(checks[0]["status"], "UP")
        self.assertEqual(checks[0]["latency_ms"], 12.5)
        self.assertIsNone(checks[0]["error"])
        self.assertIn("checked_at", checks[0])

    def test_check_history_for_missing_monitor_returns_404(self):
        response = self.client.get("/monitors/999/checks")

        self.assertEqual(response.status_code, 404)



    def test_update_monitor_name(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Old Name",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.patch(
            f"/monitors/{monitor_id}",
            json={"name": "New Name"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["monitor"]["name"], "New Name")
        self.assertEqual(response.json()["monitor"]["target"], "127.0.0.1")
        self.assertEqual(response.json()["monitor"]["monitor_type"], "ping")

    def test_update_monitor_target(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Example",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.patch(
            f"/monitors/{monitor_id}",
            json={"target": "192.168.1.1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["monitor"]["target"],
            "192.168.1.1",
        )

    def test_update_monitor_type_and_normalize_target(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Example",
                "target": "example.com",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.patch(
            f"/monitors/{monitor_id}",
            json={"monitor_type": "http"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["monitor"]["monitor_type"], "http")
        self.assertEqual(
            response.json()["monitor"]["target"],
            "https://example.com",
        )

    def test_update_missing_monitor_returns_404(self):
        response = self.client.patch(
            "/monitors/999",
            json={"name": "New Name"},
        )

        self.assertEqual(response.status_code, 404)

    def test_update_monitor_with_invalid_type_returns_422(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Example",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.patch(
            f"/monitors/{monitor_id}",
            json={"monitor_type": "ftp"},
        )

        self.assertEqual(response.status_code, 422)

    def test_update_monitor_with_empty_body_returns_422(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Example",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = create_response.json()["id"]

        response = self.client.patch(
            f"/monitors/{monitor_id}",
            json={},
        )

        self.assertEqual(response.status_code, 422)



    def test_create_tcp_monitor(self):
        response = self.client.post(
            "/monitors",
            json={
                "name": "TCP Localhost",
                "target": "127.0.0.1",
                "monitor_type": "tcp",
                "port": 8080,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["monitor_type"], "tcp")
        self.assertEqual(response.json()["port"], 8080)

    def test_create_tcp_monitor_without_port_returns_422(self):
        response = self.client.post(
            "/monitors",
            json={
                "name": "TCP Localhost",
                "target": "127.0.0.1",
                "monitor_type": "tcp",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_update_tcp_monitor_port(self):
        create_response = self.client.post(
            "/monitors",
            json={
                "name": "TCP Localhost",
                "target": "127.0.0.1",
                "monitor_type": "tcp",
                "port": 8080,
            },
        )
        self.assertEqual(create_response.status_code, 201)
        monitor_id = create_response.json()["id"]

        response = self.client.patch(
            f"/monitors/{monitor_id}",
            json={"port": 9090},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["monitor"]["port"], 9090)

    @patch("api.check_tcp")
    def test_run_tcp_check(self, mock_check_tcp):
        mock_check_tcp.return_value = {
            "status": "UP",
            "latency_ms": 5.2,
            "error": None,
        }

        create_response = self.client.post(
            "/monitors",
            json={
                "name": "TCP Localhost",
                "target": "127.0.0.1",
                "monitor_type": "tcp",
                "port": 8080,
            },
        )
        self.assertEqual(create_response.status_code, 201)
        monitor_id = create_response.json()["id"]

        response = self.client.post(f"/monitors/{monitor_id}/check")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["check"]["status"], "UP")
        mock_check_tcp.assert_called_once_with("127.0.0.1", 8080)



    def test_create_tcp_monitor_with_invalid_port_returns_422(self):
        for port in [0, 65536]:
            with self.subTest(port=port):
                response = self.client.post(
                    "/monitors",
                    json={
                        "name": "Invalid TCP",
                        "target": "127.0.0.1",
                        "monitor_type": "tcp",
                        "port": port,
                    },
                )

                self.assertEqual(response.status_code, 422)

    def test_create_ping_monitor_with_port_returns_422(self):
        response = self.client.post(
            "/monitors",
            json={
                "name": "Ping Localhost",
                "target": "127.0.0.1",
                "monitor_type": "ping",
                "port": 8080,
            },
        )

        self.assertEqual(response.status_code, 422)


    @patch("api.check_container")
    def test_automatic_monitoring_runs_docker_check(
        self, mock_check_container
    ):
        mock_check_container.return_value = {
            "status": "UP",
            "latency_ms": 3.5,
            "error": None,
        }

        create_response = self.client.post(
            "/monitors",
            json={
                "name": "Docker Test",
                "target": "test-container",
                "monitor_type": "docker",
            },
        )
        self.assertEqual(create_response.status_code, 201)

        import asyncio

        async def run_one_cycle():
            task = asyncio.create_task(api.automatic_monitoring())

            for _ in range(100):
                if mock_check_container.called:
                    break
                await asyncio.sleep(0.01)

            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        asyncio.run(run_one_cycle())

        mock_check_container.assert_called_once_with("test-container")

        history_response = self.client.get(
            f"/monitors/{create_response.json()['id']}/checks"
        )
        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(len(history_response.json()["checks"]), 1)
        self.assertEqual(
            history_response.json()["checks"][0]["status"], "UP"
        )




    @patch("api.check_tcp")
    def test_automatic_monitoring_runs_tcp_check(self, mock_check_tcp):
        mock_check_tcp.return_value = {
            "status": "UP",
            "latency_ms": 4.5,
            "error": None,
        }

        create_response = self.client.post(
            "/monitors",
            json={
                "name": "TCP Localhost",
                "target": "127.0.0.1",
                "monitor_type": "tcp",
                "port": 8080,
            },
        )
        self.assertEqual(create_response.status_code, 201)

        import asyncio

        async def run_one_cycle():
            task = asyncio.create_task(api.automatic_monitoring())

            # Döngünün ilk kontrolü tamamlanana kadar bekle.
            for _ in range(100):
                if mock_check_tcp.called:
                    break
                await asyncio.sleep(0.01)

            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        asyncio.run(run_one_cycle())

        mock_check_tcp.assert_called_once_with("127.0.0.1", 8080)

        history_response = self.client.get(
            f"/monitors/{create_response.json()['id']}/checks"
        )
        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(len(history_response.json()["checks"]), 1)
        self.assertEqual(history_response.json()["checks"][0]["status"], "UP")


    @patch("api.check_ping")
    def test_monitor_stats(self, mock_check_ping):
        mock_check_ping.side_effect = [
            {"status": "UP", "latency_ms": 10.0, "error": None},
            {"status": "DOWN", "latency_ms": None, "error": "Timeout"},
            {"status": "UP", "latency_ms": 20.0, "error": None},
        ]

        response = self.client.post(
            "/monitors",
            json={
                "name": "Stats Test",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = response.json()["id"]

        for _ in range(3):
            self.client.post(f"/monitors/{monitor_id}/check")

        stats_response = self.client.get(
            f"/monitors/{monitor_id}/stats"
        )

        self.assertEqual(stats_response.status_code, 200)
        stats = stats_response.json()
        self.assertEqual(stats["total_checks"], 3)
        self.assertEqual(stats["up_checks"], 2)
        self.assertEqual(stats["down_checks"], 1)
        self.assertEqual(stats["success_rate"], 66.67)
        self.assertEqual(stats["avg_latency_ms"], 15.0)
        self.assertIsNotNone(stats["first_check_at"])
        self.assertIsNotNone(stats["last_check_at"])

    def test_monitor_stats_without_checks(self):
        response = self.client.post(
            "/monitors",
            json={
                "name": "Empty Stats",
                "target": "127.0.0.1",
                "monitor_type": "ping",
            },
        )
        monitor_id = response.json()["id"]

        stats_response = self.client.get(
            f"/monitors/{monitor_id}/stats"
        )

        self.assertEqual(stats_response.status_code, 200)
        stats = stats_response.json()
        self.assertEqual(stats["total_checks"], 0)
        self.assertEqual(stats["up_checks"], 0)
        self.assertEqual(stats["down_checks"], 0)
        self.assertEqual(stats["success_rate"], 0.0)
        self.assertIsNone(stats["avg_latency_ms"])
        self.assertIsNone(stats["first_check_at"])
        self.assertIsNone(stats["last_check_at"])


if __name__ == "__main__":
    unittest.main()
