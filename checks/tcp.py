
import socket
import time


def check_tcp(target: str, port: int, timeout_seconds: int = 3) -> dict:
    """Check whether a TCP connection can be established."""

    if not target or not target.strip():
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Target cannot be empty",
        }

    if not 1 <= port <= 65535:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Port must be between 1 and 65535",
        }

    if timeout_seconds < 1:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Timeout must be at least 1 second",
        }

    target = target.strip()
    start = time.perf_counter()

    try:
        with socket.create_connection(
            (target, port),
            timeout=timeout_seconds,
        ):
            latency_ms = round(
                (time.perf_counter() - start) * 1000, 2
            )

        return {
            "status": "UP",
            "latency_ms": latency_ms,
            "error": None,
        }

    except (OSError, socket.timeout) as exc:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": f"TCP connection failed: {exc}",
        }
