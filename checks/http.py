
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse


def check_http(url: str, timeout_seconds: int = 5) -> dict:
    """Check an HTTP or HTTPS endpoint."""

    if not url or not url.strip():
        return {
            "status": "DOWN",
            "latency_ms": None,
            "http_status_code": None,
            "error": "URL cannot be empty",
        }

    if timeout_seconds < 1:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "http_status_code": None,
            "error": "Timeout must be at least 1 second",
        }

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "http_status_code": None,
            "error": "A valid HTTP or HTTPS URL is required",
        }

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "MonitoringPlatform/0.2"},
        method="GET",
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout_seconds,
        ) as response:
            status_code = response.status

        latency_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        is_up = 200 <= status_code < 400

        return {
            "status": "UP" if is_up else "DOWN",
            "latency_ms": latency_ms,
            "http_status_code": status_code,
            "error": None if is_up else f"HTTP status {status_code}",
        }

    except urllib.error.HTTPError as exc:
        latency_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        return {
            "status": "DOWN",
            "latency_ms": latency_ms,
            "http_status_code": exc.code,
            "error": f"HTTP status {exc.code}",
        }

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "http_status_code": None,
            "error": f"Connection error: {exc}",
        }

    except ValueError as exc:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "http_status_code": None,
            "error": f"Invalid URL: {exc}",
        }
