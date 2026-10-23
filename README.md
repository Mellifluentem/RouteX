# RouteX

A lightweight, modular, self-hosted monitoring platform for checking host, web service, TCP port, and Docker container availability.

**Motto:** Monitor anything you can reach.

## Features

- Ping-based host monitoring
- HTTP/HTTPS monitoring
- TCP port monitoring
- Docker container monitoring
- UP/DOWN status detection
- Latency and error reporting
- REST API built with FastAPI
- SQLite database integration
- Persistent monitoring check history
- Enable and disable monitors from the web dashboard
- Edit and delete monitors
- Automatic background monitoring every 60 seconds
- Web dashboard for managing and viewing monitors
- Manual checks and monitoring history
- Per-monitor statistics endpoint
- Total, UP, and DOWN check counts
- Check success rate and average latency
- First and last recorded check timestamps

## Technologies

- Python
- FastAPI
- SQLite
- Docker SDK for Python
- HTML, CSS, JavaScript
- Uvicorn

## Project Status

RouteX is currently in **beta development**. Features and functionality may change as development continues. The project is not yet considered stable or production-ready.

## Development Roadmap

- [x] V0.1 — Ping monitoring
- [x] V0.2 — HTTP/HTTPS monitoring
- [x] V0.3 — FastAPI REST API
- [x] V0.4 — SQLite integration
- [x] V0.5 — Monitoring check history
- [x] V0.6 — Automatic monitoring and monitor enable/disable controls
- [x] V0.7 — Web dashboard improvements and monitor management
- [x] V0.8 — TCP port monitoring
- [x] V0.9 — Docker container monitoring
- [x] V0.10 — Monitoring statistics and history metrics API
- [ ] V0.11 — Dashboard visualization and UI/UX improvements
- [ ] V1.0 — Installation, configuration, backup/restore, and reliability improvements
- [ ] Future — Agent-based monitoring

## Getting Started

### Requirements

- Python 3.10 or newer
- Git
- Python dependencies listed in `requirements.txt`
- Docker Engine or another compatible Docker endpoint for Docker monitoring

### Installation

Clone the repository:

```bash
git clone https://github.com/Mellifluentem/RouteX.git
cd RouteX
```

Create and activate a virtual environment.

**Linux (Fish shell):**

```fish
python -m venv .venv
source .venv/bin/activate.fish
```

**Linux / macOS (Bash or Zsh):**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn api:app --reload
```

Open the dashboard at:

http://127.0.0.1:8000

The API documentation is available at:

http://127.0.0.1:8000/docs

### Docker Monitoring

Docker monitoring requires RouteX to be able to connect to a Docker Engine. Configure Docker access for the environment running RouteX before creating Docker monitors in the dashboard.

For a Docker monitor, use a container name or ID as the target. RouteX reports whether the container is running and records check results in its monitoring history.

## Tests

The current test suite has **43 passing tests**

## Goal

RouteX aims to provide a modular, self-hosted monitoring platform for hosts and web services, with future support for agent-based devices.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 RouteX Team.
