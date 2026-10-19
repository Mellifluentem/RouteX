
from unittest.mock import patch

from checks.tcp import check_tcp


def test_tcp_rejects_empty_target():
    result = check_tcp("", 80)

    assert result["status"] == "DOWN"
    assert result["latency_ms"] is None
    assert result["error"] == "Target cannot be empty"


def test_tcp_rejects_invalid_port():
    result = check_tcp("127.0.0.1", 0)

    assert result["status"] == "DOWN"
    assert result["latency_ms"] is None
    assert result["error"] == "Port must be between 1 and 65535"


def test_tcp_rejects_port_above_maximum():
    result = check_tcp("127.0.0.1", 65536)

    assert result["status"] == "DOWN"
    assert result["latency_ms"] is None
    assert result["error"] == "Port must be between 1 and 65535"


def test_tcp_rejects_invalid_timeout():
    result = check_tcp("127.0.0.1", 80, timeout_seconds=0)

    assert result["status"] == "DOWN"
    assert result["latency_ms"] is None
    assert result["error"] == "Timeout must be at least 1 second"


def test_tcp_successful_connection():
    with patch("checks.tcp.socket.create_connection") as mock_connect:
        result = check_tcp("127.0.0.1", 443)

    assert result["status"] == "UP"
    assert isinstance(result["latency_ms"], float)
    assert result["error"] is None
    mock_connect.assert_called_once_with(("127.0.0.1", 443), timeout=3)


def test_tcp_failed_connection():
    with patch(
        "checks.tcp.socket.create_connection",
        side_effect=ConnectionRefusedError("Connection refused"),
    ):
        result = check_tcp("127.0.0.1", 443)

    assert result["status"] == "DOWN"
    assert result["latency_ms"] is None
    assert "TCP connection failed" in result["error"]
