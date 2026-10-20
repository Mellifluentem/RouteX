
from unittest.mock import MagicMock, patch

from docker.errors import NotFound

from checks.docker_check import check_container, list_containers


def test_list_containers_returns_container_details():
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.short_id = "abc123"
    mock_container.name = "test-container"
    mock_container.status = "running"

    mock_client.containers.list.return_value = [mock_container]

    with patch(
        "checks.docker_check.docker.from_env",
        return_value=mock_client,
    ):
        result = list_containers()

    assert result == [
        {
            "id": "abc123",
            "name": "test-container",
            "status": "running",
        }
    ]
    mock_client.close.assert_called_once()


def test_list_containers_returns_empty_list():
    mock_client = MagicMock()
    mock_client.containers.list.return_value = []

    with patch(
        "checks.docker_check.docker.from_env",
        return_value=mock_client,
    ):
        result = list_containers()

    assert result == []
    mock_client.close.assert_called_once()


def test_check_container_running():
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.status = "running"
    mock_client.containers.get.return_value = mock_container

    with patch(
        "checks.docker_check.docker.from_env",
        return_value=mock_client,
    ):
        result = check_container("abc123")

    assert result["status"] == "UP"
    assert isinstance(result["latency_ms"], float)
    assert result["error"] is None
    mock_container.reload.assert_called_once()
    mock_client.close.assert_called_once()


def test_check_container_stopped():
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.status = "exited"
    mock_client.containers.get.return_value = mock_container

    with patch(
        "checks.docker_check.docker.from_env",
        return_value=mock_client,
    ):
        result = check_container("abc123")

    assert result["status"] == "DOWN"
    assert result["error"] == "Container is exited"
    mock_client.close.assert_called_once()


def test_check_container_rejects_empty_id():
    result = check_container("")

    assert result["status"] == "DOWN"
    assert result["latency_ms"] is None
    assert result["error"] == "Container ID cannot be empty"


def test_check_container_not_found():
    mock_client = MagicMock()
    mock_client.containers.get.side_effect = NotFound("Not found")

    with patch(
        "checks.docker_check.docker.from_env",
        return_value=mock_client,
    ):
        result = check_container("missing-container")

    assert result["status"] == "DOWN"
    assert result["latency_ms"] is None
    assert result["error"] == "Container not found"
    mock_client.close.assert_called_once()
