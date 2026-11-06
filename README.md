# 🗺️ Maps of Power

<p align="center">
  <img src="storage/media/images/mop_logo.svg" alt="Maps of Power Logo" width="180px" style="margin-bottom: 20px;" />
</p>

<p align="center">
  <a href="https://github.com/BernhardKoschicek/maps-of-power/actions/workflows/ci-security.yml">
    <img src="https://github.com/BernhardKoschicek/maps-of-power/actions/workflows/ci-security.yml/badge.svg" alt="CI & Security Status" />
  </a>
  <a href="badges/coverage.svg">
    <img src="badges/coverage.svg" alt="Test Coverage" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License" />
  </a>
  <img src="https://img.shields.io/badge/python-3.13+-blue.svg?style=flat-square" alt="Python Versions" />
  <img src="https://img.shields.io/badge/podman-ready-purple.svg?style=flat-square" alt="Podman Ready" />
</p>

---

The research initiative **Maps of Power** serves the methodological and interdisciplinary networking of scholars in the field of *Historical Geography*.

Founded in 2019 under the title **"Maps of Power: Historical Atlas of Places, Borderzones and Migration Dynamics in Byzantium (TIB Balkans)"**, it emerged from the idea of deepening historical-geographical research methodologically and broadening it thematically.

Building on the long-running project **[Tabula Imperii Byzantini (TIB)](https://tib.oeaw.ac.at/)** — conducted at the *Austrian Academy of Sciences (ÖAW, Vienna)* since 1966 — the initiative aims to expand the spatial focus of the TIB beyond the Byzantine world to include other European regions of the Middle Ages.

The successfully completed cluster project **["Digitising Patterns of Power (DPP): Peripherical Mountains in the Medieval World"](https://dpp.oeaw.ac.at/)** serves as a methodological and conceptual precursor.

---

## 🚀 Key Features

*   **Interactive Maps & Exploration**: High-fidelity mapping of historical regions, borderzones, toponyms, and migration dynamics.
*   **Digital TIB Hub**: Integrated digital edition of Tabula Imperii Byzantini volumes, interactive registers, toponym search, and modern HTML5 book reader.
*   **Container-Ready (Podman & Docker)**: Rootless, daemonless OCI containers (`Containerfile`, `compose.yaml`) with unprivileged user UID 1000 and Redis caching.
*   **Separated & Scalable Media Storage**: Clean distinction between code and persistent data (`storage/data/` for SQLite, `storage/media/` for high-res book scans, images, and repository PDFs).
*   **Automated Thumbnails**: Zero-overhead incremental thumbnail generator via Pillow with Git hooks (`post-merge`, `post-checkout`) and on-demand Flask fallback.
*   **Continuous Deployment Pipeline**: Push-based GitHub Actions deployment workflow (`.github/workflows/deploy.yml`) and server-side update automation (`scripts/deploy.sh`).
*   **Rigorous Quality Assurance**: 100% test pass rate with **93.5%+** coverage, strict typing (`mypy`), and SAST security audits (`bandit`, `pip-audit`).

---

## ⚡ Quick Start

### Option 1: Local Development (with `uv`)

Prerequisites: Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
# 1. Clone repository
git clone https://github.com/BernhardKoschicek/maps-of-power.git
cd maps-of-power

# 2. Install dependencies into virtual environment
uv sync

# 3. Install Git hooks (automatically manages thumbnails on pull)
uv run python scripts/setup_git_hooks.py

# 4. Start local development server
uv run python runserver.py
```
Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

---

### Option 2: Containerized (with `podman compose`)

Prerequisites: [Podman](https://podman.io/) (available via `apt install podman podman-compose`).

```bash
# Build and start Maps of Power + Redis cache in background
podman compose up -d

# Check logs
podman compose logs -f

# Verify health
curl http://127.0.0.1:5000/health
```

---

## 📖 Production Deployment Guide

For comprehensive, step-by-step instructions on deploying Maps of Power in production on Debian / Ubuntu servers — including **Nginx reverse proxy**, **Let's Encrypt SSL**, **systemd service configuration**, and **automated CI/CD pipelines** — please read:

👉 **[docs/INSTALL.md — Complete Production Deployment Guide](docs/INSTALL.md)**

---

## 🧪 Tests & Quality Assurance

### Run Test Suite & Coverage
```bash
uv run pytest --cov=. --cov-report=term-missing
```

### Static Type Checking (`mypy`)
```bash
uv run mypy mop scripts runserver.py gunicorn.conf.py
```

### Code Linter (`pylint`)
```bash
uv run pylint mop gunicorn.conf.py
```

### Security Audits (`bandit` & `pip-audit`)
```bash
# Static application security testing (SAST)
uvx bandit -r . -ll -x ./.venv,./tests

# Dependency vulnerability scanning (CVEs)
uv export --all-groups --output-file requirements.txt
uvx pip-audit -r requirements.txt --disable-pip
rm -f requirements.txt
```

---

## 📁 Project Structure

```
maps-of-power/
├── Containerfile           # Multi-stage OCI/Podman container definition
├── compose.yaml            # Podman Compose service definition (Web + Redis)
├── gunicorn.conf.py        # Production Gunicorn WSGI configuration
├── mop.wsgi                # Apache mod_wsgi entry point
├── config.py               # 12-factor application configuration
├── pyproject.toml          # Project dependencies & tool configurations (pytest, mypy, pylint, coverage)
├── uv.lock                 # Deterministic dependency lockfile
├── docs/                   # Documentation
│   ├── INSTALL.md          # Production installation & Debian setup guide
│   └── STYLE_GUIDE.md      # Code and UI style guidelines
├── mop/                    # Core application package
│   ├── data/               # Structured metadata, projects, and narratives
│   ├── display/            # Image gallery & dynamic thumbnail generation
│   ├── model/              # Data models, TIB SQLite database & OpenAtlas API
│   ├── static/             # UI static assets (CSS, JS, fonts, SVGs)
│   ├── templates/          # Jinja2 templates (overview, TIB, reader, views)
│   ├── tib_views.py        # Tabula Imperii Byzantini routes & reader API
│   ├── views.py            # Main application routes & media serving
│   └── ...
├── storage/                # Persistent data directory
│   ├── data/               # SQLite database (tib_register.db)
│   └── media/              # Media assets (books/, images/, repository/, thumbnails/)
├── scripts/                # Automation utilities
│   ├── entrypoint.sh       # Container startup & directory initialization
│   ├── deploy.sh           # Automated deployment & pull update script
│   ├── setup_git_hooks.py  # Git hooks installer (post-merge / post-checkout)
│   ├── thumbnail_generation.py # Incremental Pillow thumbnail generator
│   └── build_tib_db.py     # TIB database builder
├── tests/                  # Pytest integration, unit, and functional test suites
└── .github/workflows/      # GitHub Actions CI/CD workflows
    ├── ci-security.yml     # Tests, mypy, security audits, and container build
    └── deploy.yml          # Automated deployment to production server via SSH
```

---

## 📄 License

This project is open-source and licensed under the **[MIT License](LICENSE)**.

---

## 🧑‍💻 Authors & Credits

*   Developed and maintained by the **Maps of Power** research group.
*   Hosted and supported by the **Austrian Academy of Sciences (ÖAW)**.
*   Precursor methodologies courtesy of **Digitising Patterns of Power (DPP)**.
