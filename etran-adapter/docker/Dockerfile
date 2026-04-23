FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev libxslt1-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY alembic/ alembic/
COPY alembic.ini .
COPY src/ src/

# --- API ---
FROM base AS api
EXPOSE 8000
CMD ["uvicorn", "etran_adapter.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- RQ Worker ---
FROM base AS worker
CMD ["python", "-m", "etran_adapter.queue.worker"]
