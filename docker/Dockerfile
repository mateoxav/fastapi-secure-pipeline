# syntax=docker/dockerfile:1

# --- Builder stage ---
# Specific version for reproducibility
FROM python:3.12.0-slim AS builder
WORKDIR /app

# Create a virtual environment to isolate dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies into the venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Runtime stage ---
FROM python:3.12.0-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash -u 10001 appuser
COPY --from=builder /opt/venv /opt/venv

# Copy application source code
COPY ./app ./app

# Set correct ownership
RUN chown -R appuser:appuser /app
USER appuser

# Healthcheck to verify the server is running
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 8000))"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
