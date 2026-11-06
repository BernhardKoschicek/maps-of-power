#!/usr/bin/env bash
# ==============================================================================
# Maps of Power - Deployment & Update Script
# Automatically pulls the latest 'main' branch, updates dependencies/containers,
# regenerates assets/thumbnails, and performs health check validation.
# ==============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_DIR}"

echo "==> [1/5] Checking repository status in ${REPO_DIR}..."

# Fetch latest commits from origin
git fetch origin main

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

FORCE_DEPLOY="${FORCE_DEPLOY:-false}"

if [ "${LOCAL_HASH}" = "${REMOTE_HASH}" ] && [ "${FORCE_DEPLOY}" != "true" ]; then
    echo "==> Repository is already up to date with origin/main (${LOCAL_HASH:0:8})."
    echo "    (Set FORCE_DEPLOY=true to redeploy anyway)."
    exit 0
fi

echo "==> [2/5] Updating repository (${LOCAL_HASH:0:8} -> ${REMOTE_HASH:0:8})..."
git checkout main
git pull --ff-only origin main

# Detect deployment mode: Containerized (Podman/Docker) vs Bare-Metal (systemd)
DEPLOY_MODE="${DEPLOY_MODE:-auto}"

if [ "${DEPLOY_MODE}" = "auto" ]; then
    if command -v podman >/dev/null 2>&1 && podman ps --format "{{.Names}}" 2>/dev/null | grep -q "maps-of-power"; then
        DEPLOY_MODE="container"
    elif command -v docker >/dev/null 2>&1 && docker ps --format "{{.Names}}" 2>/dev/null | grep -q "maps-of-power"; then
        DEPLOY_MODE="container"
    else
        DEPLOY_MODE="baremetal"
    fi
fi

echo "==> [3/5] Applying updates (Mode: ${DEPLOY_MODE})..."

# Ensure git hooks are installed regardless of deployment mode
if command -v python3 >/dev/null 2>&1; then
    python3 scripts/setup_git_hooks.py || true
fi

if [ "${DEPLOY_MODE}" = "container" ]; then
    echo "==> Building and restarting container services via compose..."
    if command -v podman >/dev/null 2>&1 && podman compose version >/dev/null 2>&1; then
        podman compose up -d --build
    elif command -v podman-compose >/dev/null 2>&1; then
        podman-compose up -d --build
    elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
        docker compose up -d --build
    else
        echo "ERROR: Neither podman compose nor docker compose found!" >&2
        exit 1
    fi
else
    echo "==> Updating Python virtual environment with uv..."
    if command -v uv >/dev/null 2>&1; then
        uv sync --frozen --no-dev
        uv run python scripts/setup_git_hooks.py
        uv run python scripts/thumbnail_generation.py
    else
        echo "ERROR: uv package manager not found. Please install uv (curl -LsSf https://astral.sh/uv/install.sh | sh)." >&2
        exit 1
    fi

    echo "==> Restarting maps-of-power service..."
    if systemctl is-active --quiet maps-of-power.service 2>/dev/null; then
        sudo systemctl restart maps-of-power.service
    elif systemctl --user is-active --quiet maps-of-power.service 2>/dev/null; then
        systemctl --user restart maps-of-power.service
    else
        echo "Notice: maps-of-power systemd service not currently active. Skipping restart."
    fi
fi

echo "==> [4/5] Waiting for application to be ready..."
sleep 3

HEALTH_PORT="${PORT:-5000}"
HEALTH_URL="http://127.0.0.1:${HEALTH_PORT}/health"

echo "==> [5/5] Performing healthcheck against ${HEALTH_URL}..."
if curl -sf "${HEALTH_URL}" >/dev/null 2>&1; then
    echo "SUCCESS: Maps of Power is healthy and up-to-date at commit $(git rev-parse --short HEAD)!"
else
    echo "WARNING: Healthcheck failed at ${HEALTH_URL}. Check logs for details:" >&2
    if [ "${DEPLOY_MODE}" = "container" ]; then
        podman logs maps-of-power --tail 30 2>/dev/null || docker logs maps-of-power --tail 30 2>/dev/null || true
    else
        journalctl -u maps-of-power.service -n 30 --no-pager 2>/dev/null || true
    fi
    exit 1
fi
