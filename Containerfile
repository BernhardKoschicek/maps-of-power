# Stage 1: Build virtual environment with uv
FROM python:3.13-slim-bookworm AS builder

# Install uv for fast, deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY mop/ mop/
COPY scripts/ scripts/
COPY config.py runserver.py gunicorn.conf.py entrypoint.sh ./

# Finalize venv with project code
RUN uv sync --frozen --no-dev


# Stage 2: Minimal runtime image
FROM python:3.13-slim-bookworm AS runtime

# Install curl for container healthchecks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create unprivileged user (UID/GID 1000 matches standard host user for rootless Podman)
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -d /app -s /bin/sh appuser

WORKDIR /app

# Copy application and pre-built virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app /app

# Create default storage directories with proper ownership
RUN mkdir -p /app/storage/data \
             /app/storage/media/images \
             /app/storage/media/thumbnails \
             /app/storage/media/books \
             /app/storage/media/repository && \
    chown -R appuser:appuser /app/storage && \
    chmod +x /app/entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STORAGE_DIR=/app/storage \
    PORT=5000

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "mop:app"]
