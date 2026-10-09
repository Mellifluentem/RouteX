import platform
import subprocess
import time


def check_ping(target: str, timeout_seconds: int = 2) -> dict:
    """Check whether a host responds to a ping request."""

    if not target or not target.strip():
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Target cannot be empty",
        }

    if timeout_seconds < 1:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Timeout must be at least 1 second",
        }

    target = target.strip()
    system = platform.system()

    if system == "Windows":
        command = [
            "ping", "-n", "1",
            "-w", str(timeout_seconds * 1000),
            target,
        ]
    elif system == "Linux":
        command = [
            "ping", "-c", "1",
            "-W", str(timeout_seconds),
            target,
        ]
    else:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": f"Unsupported operating system: {system}",
        }

    start = time.perf_counter()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 2,
            check=False,
        )

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        if result.returncode == 0:
            return {
                "status": "UP",
                "latency_ms": elapsed_ms,
                "error": None,
            }

        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "No ping reply received",
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Ping command timed out",
        }

    except OSError as exc:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": f"Could not execute ping: {exc}",
        }
