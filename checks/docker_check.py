
import time

import docker
from docker.errors import DockerException, NotFound


def list_containers() -> list[dict]:
    """List Docker containers, including stopped containers."""

    try:
        client = docker.from_env()

        try:
            containers = client.containers.list(all=True)

            return [
                {
                    "id": container.short_id,
                    "name": container.name,
                    "status": container.status,
                }
                for container in containers
            ]
        finally:
            client.close()

    except DockerException as exc:
        raise RuntimeError(f"Could not connect to Docker: {exc}") from exc


def check_container(container_id: str) -> dict:
    """Check whether a Docker container is running."""

    if not container_id or not container_id.strip():
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Container ID cannot be empty",
        }

    start = time.perf_counter()

    try:
        client = docker.from_env()

        try:
            container = client.containers.get(container_id.strip())
            container.reload()

            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            if container.status == "running":
                return {
                    "status": "UP",
                    "latency_ms": latency_ms,
                    "error": None,
                }

            return {
                "status": "DOWN",
                "latency_ms": latency_ms,
                "error": f"Container is {container.status}",
            }
        finally:
            client.close()

    except NotFound:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": "Container not found",
        }

    except DockerException as exc:
        return {
            "status": "DOWN",
            "latency_ms": None,
            "error": f"Docker check failed: {exc}",
        }
