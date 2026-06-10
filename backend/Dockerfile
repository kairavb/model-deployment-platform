FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY deployment_engine /app/deployment_engine
COPY backend /app/backend

WORKDIR /app/deployment_engine
RUN pip install --no-cache-dir .

WORKDIR /app/backend
RUN pip install --no-cache-dir .

RUN mkdir -p /storage/models /storage/builds

FROM base AS development
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

FROM base AS production
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
