# Cloud-Native AI Deployment Platform

Local-first platform for uploading ML models, deploying them as inference services, and managing their lifecycle through a web dashboard.

## Repository Layout

```
ai-platform/
├── backend/              # FastAPI monolith
├── deployment_engine/    # Docker deployment engine (imported by backend)
├── frontend/             # React + TypeScript dashboard
├── docs/                 # Architecture and design docs
├── inference/            # Inference server image templates
├── infra/                # Prometheus and future Grafana config
├── scripts/                # Utility scripts
└── storage/models/       # Uploaded model artifacts (gitignored)
```

## Quick Start

1. Copy environment file:

```bash
cp .env.example .env
```

2. Initialize local storage:

```bash
./scripts/init-storage.sh
```

3. Start the platform:

```bash
docker compose up --build
```

4. Development mode with hot reload:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Services

| Service    | URL                     |
|-----------|-------------------------|
| Frontend  | http://localhost:3000   |
| Backend   | http://localhost:8000   |
| API Docs  | http://localhost:8000/docs |
| Prometheus| http://localhost:9090   |

## Status

This repository contains project scaffolding only. Business logic is intentionally not implemented yet.

Implementation phases are documented in `docs/ARCHITECTURE.md`.

## Tech Stack

- Frontend: React, TypeScript, TailwindCSS
- Backend: FastAPI, Python
- Database: PostgreSQL
- Deployment: Docker, Docker Compose
- Monitoring: Prometheus (Grafana later)
