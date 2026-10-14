# 📦 Installation & Production Deployment Guide

This guide covers setting up **Maps of Power** on a Debian-based server (Debian 12 Bookworm, Ubuntu 22.04+, or similar) using **standard Debian packages** to minimize maintenance overhead.

You can choose between two deployment methods:
- **[Method A: Containerized Deployment (Podman Compose)](#-method-a-containerized-deployment-podman--podman-compose-recommended)** *(Recommended)* — Isolated, rootless, reproducible, includes Redis.
- **[Method B: Bare-Metal Deployment (Debian + Systemd)](#-method-b-bare-metal-deployment-debian--systemd)** — Runs natively via `uv` and a systemd unit.

Both methods use **Nginx** (installed from Debian packages) as reverse proxy with **Let's Encrypt** SSL.

---

## 📑 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Method A: Containerized Deployment (Podman)](#-method-a-containerized-deployment-podman--podman-compose-recommended)
3. [Method B: Bare-Metal Deployment (Debian + Systemd)](#-method-b-bare-metal-deployment-debian--systemd)
4. [Reverse Proxy Setup (Nginx & SSL)](#-reverse-proxy-setup-standard-debian-nginx)
5. [Automated CI/CD & Deployment Pipeline](#-automated-cicd--deployment-pipeline)
6. [Maintenance & Backups](#-maintenance--backups)

---

## 🏛️ Architecture Overview

```
Internet (HTTP:80 / HTTPS:443)
           │
           ▼
┌──────────────────────────────────────────────┐
│  Nginx Reverse Proxy (Debian standard pkg)   │
│  - SSL Termination (Let's Encrypt / Certbot) │
│  - Security headers & Gzip compression       │
└──────────────────────┬───────────────────────┘
                       │  http://127.0.0.1:5000
                       ▼
┌──────────────────────────────────────────────┐
│  Maps of Power Backend (Gunicorn + Flask)    │
│  - Port 5000 (Internal)                      │
│  - /health endpoint                          │
├──────────────────────┬───────────────────────┤
│  Persistent Storage  │  Caching Layer        │
│  ./storage/data/     │  Redis (:6379)        │
│  ./storage/media/    │                       │
└──────────────────────┴───────────────────────┘
```

---

## 🐳 Method A: Containerized Deployment (Podman & Podman Compose) *(Recommended)*

Using **Podman** allows running the application in a rootless, isolated container environment without needing root privileges or a persistent daemon.

### 1. Install Podman on Debian
Debian 12 includes Podman in its official repositories:
```bash
sudo apt update
sudo apt install -y podman podman-compose curl git
```

### 2. Clone the Repository
Clone into your target directory (e.g. `/var/www/maps-of-power` or your user home `/home/bkoschicek/www/maps-of-power`):
```bash
git clone https://github.com/BernhardKoschicek/maps-of-power.git /var/www/maps-of-power
cd /var/www/maps-of-power
```

### 3. Ensure Storage Directories & Permissions
The container runs as non-root user `appuser` (UID 1000). Ensure the storage folders exist:
```bash
mkdir -p storage/data \
         storage/media/images \
         storage/media/thumbnails \
         storage/media/books \
         storage/media/repository
```

Place your SQLite database `tib_register.db` in `storage/data/` and high-res book scans in `storage/media/books/`.

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```bash
cat << 'EOF' > .env
SECRET_KEY=change-this-to-a-secure-random-secret-key-32-chars
CACHE_TYPE=RedisCache
CACHE_REDIS_URL=redis://redis:6379/0
WEB_CONCURRENCY=3
THREADS=2
PORT=5000
EOF
```

### 5. Build & Start with Podman Compose
```bash
# Build image and start services (Maps of Power + Redis) in detached mode
podman compose up -d --build

# Verify running containers
podman compose ps

# Check application logs
podman compose logs -f web
```

### 6. Verify Healthcheck
```bash
curl -i http://127.0.0.1:5000/health
# Response: {"status":"ok","version":"0.1.0"}
```

### 7. Autostart on Server Boot (Systemd User Service)
To ensure the container restarts automatically on server reboots without root:
```bash
# Enable linger so user services run even when logged out
loginctl enable-linger $USER

# Generate systemd unit for the container pod
mkdir -p ~/.config/systemd/user
podman generate systemd --new --name maps-of-power -f
mv container-maps-of-power.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now container-maps-of-power.service
```

---

## 🖥️ Method B: Bare-Metal Deployment (Debian + Systemd)

If you prefer running directly on Debian without containers:

### 1. Install Standard Debian Packages
```bash
sudo apt update
sudo apt install -y python3 python3-pip redis-server git curl
```

Ensure Redis is running:
```bash
sudo systemctl enable --now redis-server
```

### 2. Install `uv` (Fast Python Package Manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### 3. Clone Repository & Install Dependencies
```bash
git clone https://github.com/BernhardKoschicek/maps-of-power.git /var/www/maps-of-power
cd /var/www/maps-of-power

# Synchronize deterministic virtual environment
uv sync --frozen --no-dev

# Setup Git hooks (automatically regenerates thumbnails on git pull)
uv run python scripts/setup_git_hooks.py

# Generate thumbnails for all media images
uv run python scripts/thumbnail_generation.py
```

### 4. Create Production Configuration
```bash
mkdir -p instance
cat << 'EOF' > instance/production.py
SECRET_KEY = 'generate-a-long-random-string-here'
DEBUG = False
CACHE_TYPE = 'RedisCache'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
EOF
```

### 5. Setup Systemd Service
Create the service unit file `/etc/systemd/system/maps-of-power.service`:
```ini
[Unit]
Description=Maps of Power Flask/Gunicorn Application
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/maps-of-power
Environment="PATH=/var/www/maps-of-power/.venv/bin:/usr/local/bin:/usr/bin"
Environment="PORT=5000"
Environment="WEB_CONCURRENCY=3"
Environment="THREADS=2"

ExecStart=/var/www/maps-of-power/.venv/bin/gunicorn --config gunicorn.conf.py mop:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=10
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now maps-of-power.service
sudo systemctl status maps-of-power.service
```

---

## 🌐 Reverse Proxy Setup (Standard Debian Nginx)

Nginx is available directly from Debian's official repository, requires zero third-party repositories, and is extremely stable and low on resource usage.

### 1. Install Nginx and Certbot
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 2. Nginx Virtual Host Configuration
Create `/etc/nginx/sites-available/maps-of-power`:
```nginx
# Upstream to Gunicorn (works for both Podman container and Systemd)
upstream maps_of_power_backend {
    server 127.0.0.1:5000;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    server_name maps-of-power.at www.maps-of-power.at;

    client_max_body_size 64M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;

    location / {
        proxy_pass http://maps_of_power_backend;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # Direct caching for health endpoint
    location = /health {
        proxy_pass http://maps_of_power_backend/health;
        access_log off;
    }
}
```

Enable the configuration:
```bash
sudo ln -s /etc/nginx/sites-available/maps-of-power /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Obtain Free SSL Certificate via Let's Encrypt
```bash
sudo certbot --nginx -d maps-of-power.at -d www.maps-of-power.at
```
Certbot will automatically configure HTTPS, HTTP-to-HTTPS redirect, and install a systemd renewal timer.

---

## 🚀 Automated CI/CD & Deployment Pipeline

You can automate updates in two ways:
1. **GitHub ➔ Server (Push-based via GitHub Actions):** Triggered automatically when code merges into `main`.
2. **Server ➔ GitHub (Pull-based via Systemd Timer):** The server checks GitHub periodically and updates itself.

Both methods use the included deployment script: [scripts/deploy.sh](file:///home/bkoschicek/www/maps-of-power/scripts/deploy.sh).

### What `scripts/deploy.sh` does:
1. Fetches `origin/main` and checks if new commits exist.
2. Fast-forwards `main`.
3. If running via **Podman**: runs `podman compose up -d --build`.
4. If running via **Bare-Metal**: runs `uv sync`, generates missing thumbnails, and reloads systemd.
5. Performs a healthcheck against `http://127.0.0.1:5000/health` to confirm successful deployment.

---

### Option 1: GitHub Actions Push Pipeline (Recommended)

When you push or merge a PR to `main`, the workflow [.github/workflows/deploy.yml](file:///home/bkoschicek/www/maps-of-power/.github/workflows/deploy.yml) automatically triggers after tests pass.

#### Setup in GitHub:
In your GitHub repository, navigate to **Settings ➔ Secrets and variables ➔ Actions** and add:
- `SERVER_HOST`: Server IP or domain (e.g. `maps-of-power.at`).
- `SERVER_USER`: SSH user on the server (e.g. `bkoschicek` or `deploy`).
- `SERVER_SSH_KEY`: Private SSH key (matching the public key in `~/.ssh/authorized_keys` on the server).
- `SERVER_PATH`: Absolute path to repository (e.g. `/var/www/maps-of-power`).
- `SERVER_PORT`: SSH port (default `22`).

---

### Option 2: Server-Side Pull Timer (Pull-based, No Incoming SSH Required)

If your server does not allow incoming SSH connections from GitHub Actions, you can configure a systemd timer on the server that checks for updates every 15 minutes:

#### 1. Create `/etc/systemd/system/maps-of-power-update.service`:
```ini
[Unit]
Description=Maps of Power Auto-Update Service
After=network-online.target

[Service]
Type=oneshot
User=bkoschicek
WorkingDirectory=/var/www/maps-of-power
ExecStart=/var/www/maps-of-power/scripts/deploy.sh
StandardOutput=journal
StandardError=journal
```

#### 2. Create `/etc/systemd/system/maps-of-power-update.timer`:
```ini
[Unit]
Description=Run Maps of Power update every 15 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
Persistent=true

[Install]
WantedBy=timers.target
```

#### 3. Enable the Timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now maps-of-power-update.timer
```

Check status anytime:
```bash
systemctl list-timers maps-of-power-update.timer
```

---

## 🛠️ Maintenance & Backups

### Healthcheck
```bash
curl http://127.0.0.1:5000/health
# {"status":"ok","version":"0.1.0"}
```

### Manual Trigger of Deployment Script
```bash
FORCE_DEPLOY=true /var/www/maps-of-power/scripts/deploy.sh
```

### Backup Persistent Data
Only the `./storage` directory contains persistent state:
```bash
# Backup SQLite DB and media assets
tar -czvf mop_storage_backup_$(date +%F).tar.gz /var/www/maps-of-power/storage/
```
The application code itself is completely stateless.
