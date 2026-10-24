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
- Manual monitoring checks
- Per-monitor statistics and history endpoints
- Total, UP, and DOWN check counts
- Check success rate and average latency
- First and last recorded check timestamps
- Visual monitoring history chart with UP/DOWN status indicators
- Estimated downtime based on recorded check history
- Responsive dashboard layout for mobile screens
- Command-line database backup, verification, and restore utility

## Technologies

- Python
- FastAPI
- SQLite
- Docker SDK for Python
- HTML, CSS, and JavaScript
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
- [x] V0.11 — Dashboard visualization, history metrics, and responsive UI improvements
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

**Windows (PowerShell):**

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note:** If PowerShell blocks virtual environment activation because of the execution policy, this does not necessarily indicate a problem with RouteX. Review the PowerShell execution policy for the current user before changing any security settings. Do not run commands that change the execution policy unless you understand their security implications.


Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn api:app --reload
```

Open the dashboard:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

## Configuration

RouteX uses SQLite to store monitor definitions and monitoring check history.

By default, the database file is `routex.db` in the project directory. Set `ROUTEX_DATABASE_PATH` to use a different database file.

**Linux (Fish shell):**

```fish
set -x ROUTEX_DATABASE_PATH /path/to/routex.db
uvicorn api:app --reload
```

**Linux / macOS (Bash or Zsh):**

```bash
export ROUTEX_DATABASE_PATH=/path/to/routex.db
uvicorn api:app --reload
```

Choose a writable location for the database. Keep database files and backups in a safe location.

## Docker Monitoring

Docker monitoring requires RouteX to connect to a Docker Engine. Configure Docker access for the environment running RouteX before creating Docker monitors.

For a Docker monitor, use a container name or ID as the target. RouteX reports whether the container is running and records check results in its monitoring history.

## Backup and Restore

RouteX includes `backup_db.py`, a command-line utility for backing up, verifying, and restoring the SQLite database.

### Create a backup

Specify a destination:

```bash
python backup_db.py backup ./routex_backup.db
```

If no destination is provided, the utility creates a timestamped backup next to the configured database file:

```bash
python backup_db.py backup
```

### Verify a backup

Check the integrity of a database or backup file:

```bash
python backup_db.py verify ./routex_backup.db
```

A successful integrity check reports `Integrity: ok`.

### Restore from a backup

```bash
python backup_db.py restore ./routex_backup.db
```

**Important safety notes:**

- Stop the RouteX application before restoring the database to avoid conflicts with active connections.
- Verify the backup before restoring it.
- The restore utility creates a separate safety backup of the current database before replacing it.
- Keep backup files in a safe location and test restoration before relying on them.
- Restore has been tested in an isolated environment; production use still requires additional operational validation.

## Tests

The current test suite contains **50 passing tests**.

Run the tests with:

```bash
python -m unittest discover -s tests
```

Check the backup utility syntax:

```bash
python -m py_compile backup_db.py
```

## Goal

RouteX aims to provide a modular, self-hosted monitoring platform for hosts and web services, with future support for agent-based devices.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 RouteX Team.
