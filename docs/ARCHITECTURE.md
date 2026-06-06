# Architecture

This document summarizes the approved architecture for the Cloud-Native AI Deployment Platform.

## Core Principles

- Single FastAPI monolith for application logic
- PostgreSQL as the only database
- Deployment engine as an in-process Python package (`deployment_engine/`)
- Inference workloads run in separate Docker containers on the host
- No microservices, Redis, Celery, RabbitMQ, Kubernetes, or cloud providers

## System Components

| Component | Role |
|-----------|------|
| `frontend/` | React dashboard for models, deployments, logs, and predictions |
| `backend/` | REST API, auth, persistence, orchestration entrypoint |
| `deployment_engine/` | Docker SDK wrapper used by the backend monolith |
| `inference/` | Pre-built inference server images (sklearn, onnx, pytorch) |
| `infra/prometheus/` | Metrics scraping configuration |

## Backend Modules

| Module | Responsibility |
|--------|----------------|
| `auth` | Registration, login, JWT |
| `models` | Model registry and version uploads |
| `deployments` | Deployment lifecycle and events |
| `inference` | Authenticated prediction proxy |
| `logs` | Container log retrieval |
| `monitoring` | Health, readiness, metrics |

## Deployment Flow

1. User uploads a model version to disk and PostgreSQL.
2. User creates a deployment for a version.
3. Backend calls `deployment_engine` to run an inference container.
4. Engine waits for `/health`, then marks deployment as running.
5. Predictions are proxied through `/api/v1/deployments/{id}/predict`.

## Database Entities

- `users`
- `ml_models`
- `model_versions`
- `deployments`
- `deployment_events`

## API Surface

Base path: `/api/v1`

- Auth: `/auth/register`, `/auth/login`, `/auth/me`
- Models: `/models`, `/models/{id}/versions`
- Deployments: `/deployments`, `/deployments/{id}/stop`
- Inference: `/deployments/{id}/predict`
- Logs: `/deployments/{id}/logs`
- Monitoring: `/health`, `/ready`, `/metrics`

## Implementation Phases

1. Auth + model upload
2. Deployment engine + sklearn inference
3. Predict proxy + playground UI
4. Logs + health monitoring
5. ONNX + PyTorch images
6. Prometheus + Grafana

See the full engineering design in the project planning conversation for detailed diagrams and rationale.
