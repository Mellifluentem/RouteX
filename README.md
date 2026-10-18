# RouteX

A lightweight, modular, self-hosted monitoring platform for checking host and web service availability.

**Motto:** Monitor anything you can reach.

## Features

- Ping-based host monitoring
- HTTP/HTTPS monitoring
- UP/DOWN status detection
- Latency and error reporting
- REST API built with FastAPI
- SQLite database integration
- Persistent monitoring check history
- Enable and disable monitors from the web dashboard
- Automatic background monitoring every 60 seconds
- Web dashboard for managing and viewing monitors
- Create, edit, and delete monitors

## Technologies

- Python
- FastAPI
- SQLite
- HTML, CSS, JavaScript
- Uvicorn

## Project Status

RouteX is under active development.

- [x] V0.1 — Ping monitoring
- [x] V0.2 — HTTP/HTTPS monitoring
- [x] V0.3 — FastAPI REST API
- [x] V0.4 — SQLite integration
- [x] V0.5 — Monitoring check history
- [x] V0.6 — Automatic monitoring and monitor enable/disable controls
- [x] V0.7 — Monitor editing through the API and web dashboard
- [ ] Future — TCP port monitoring
- [ ] Future — Docker integration
- [ ] Future — Agent-based monitoring

## Getting Started

### Requirements

- Python 3.10 or newer
- Git
- Python dependencies listed in `requirements.txt`

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

Open the web dashboard:

http://127.0.0.1:8000

API documentation is available at:

http://127.0.0.1:8000/docs

## Development Status

RouteX is currently in **beta development**. Features and functionality may change as development continues. The project is not yet considered stable or production-ready.

## Goal

RouteX aims to provide a modular, self-hosted monitoring platform for hosts and web services, with future support for TCP ports, Docker containers, and agent-based devices.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 RouteX Team
