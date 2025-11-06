# syntax=docker/dockerfile:1

# --- Builder (reproducible deps) ---
# Pinning the base image by digest ensures we always build from the exact same base layer
FROM python:3.12.0-slim@sha256:19a6235339a74eca01227b03629f63b6f5020abc21142436eced6ec3a9839a76 AS builder
WORKDIR /app

# Set env vars for python and pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Create venv
RUN python -m venv /opt/venv

# Install dependencies in a reproducible way
COPY requirements.txt .
# 1. Upgrade pip in the venv
# 2. Download all required packages (with hashes, if available) to /wheels
# 3. Install packages *only* from the /wheels directory, disabling network access
# This ensures the build is reproducible and doesn't depend on PyPI availability at build time.
RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip download -r requirements.txt -d /wheels && \
    /opt/venv/bin/pip install --no-index --find-links=/wheels -r requirements.txt

# --- Runtime stage ---
FROM python:3.12.0-slim@sha256:19a6235339a74eca01227b03629f63b6f5020abc21142436eced6ec3a9839a76
WORKDIR /app

# Set env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Create a non-root user with a specific UID for security
RUN useradd --create-home --shell /bin/bash -u 10001 appuser

# Copy the venv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source code and configs
# Use --chown to set ownership directly, avoiding an extra CHOWN layer
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./web ./web
COPY --chown=appuser:appuser ./scripts ./scripts
COPY --chown=appuser:appuser docker/entrypoint.sh ./entrypoint.sh
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser alembic ./alembic

# Add executable permissions to the entrypoint script
RUN chmod +x ./entrypoint.sh

# Switch to the non-root user
USER appuser

# Healthcheck that hits the actual application /health endpoint
# This is more reliable than a simple socket check.
# We use the 'exec' form (JSON array) to pass the python one-liner,
# as HEALTHCHECK CMD does not support heredocs.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD [ "python", "-c", "import urllib.request, sys; try: r = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5); sys.exit(0 if r.status == 200 else 1); except Exception: sys.exit(1)" ]

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]

# Use Gunicorn with Uvicorn workers for production
# This is the recommended way to run FastAPI in production
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]