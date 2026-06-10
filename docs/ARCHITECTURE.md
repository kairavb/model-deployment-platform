# Architecture

Cloud-Native AI Deployment Platform — local-first system for uploading ML models, deploying them as Dockerized inference services, and operating them through a web dashboard.

## Core Principles

- Single FastAPI monolith for application logic
- PostgreSQL as the only database
- Deployment engine as an in-process Python package (`deployment_engine/`)
- Inference workloads run in separate Docker containers on the host
- No microservices, Redis, Celery, RabbitMQ, Kubernetes, or cloud providers

## System Components

| Component | Role |
|-----------|------|
| `frontend/` | React dashboard for models, deployments, logs, analytics, and predictions |
| `backend/` | REST API, auth, persistence, orchestration entrypoint |
| `deployment_engine/` | Docker SDK wrapper used by the backend monolith |
| `inference/` | Inference server image templates (sklearn implemented; onnx/pytorch scaffolded) |
| `infra/nginx/` | Reverse proxy unifying API, docs, metrics, and dashboard on port 8080 |
| `infra/prometheus/` | Metrics scraping (backend + inference containers via file_sd) |
| `infra/grafana/` | Provisioned dashboards for platform and inference metrics |

## Backend Modules

| Module | Responsibility |
|--------|----------------|
| `auth` | Registration, login, JWT, API key management |
| `models` | Model registry, version uploads, file validation |
| `deployments` | Deployment lifecycle, events, state machine |
| `inference` | Authenticated prediction proxy, inference request logs |
| `logs` | Container log retrieval |
| `monitoring` | Platform health/readiness, per-deployment stats and metrics |
| `analytics` | Usage summaries and daily request/error trends |

## Deployment Flow

1. User uploads a model version to disk and PostgreSQL.
2. User creates a deployment for a version.
3. Backend builds a per-deployment Docker image and starts an inference container.
4. Engine waits for `/health`, then marks deployment as running.
5. Predictions are proxied through `/api/v1/deployments/{id}/predict`.
6. A background task probes running deployments every 30s and syncs Prometheus file_sd targets.

## Deployment State Machine

Status transitions are enforced in `deployments/state_machine.py`:

```
pending → starting → running
                  ↘ failed
running → stopping → stopped
        ↘ starting (redeploy)
stopped → starting (redeploy)
failed  → starting (redeploy) | stopping
```

## Database Entities

- `users`
- `api_keys`
- `ml_models`
- `model_versions`
- `deployments`
- `deployment_events`
- `inference_logs`

## API Surface

Base path: `/api/v1`

| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, API key CRUD under `/auth/api-keys` |
| Models | `GET/POST /models`, `GET/PATCH/DELETE /models/{id}`, version CRUD under `/models/{id}/versions` |
| Deployments | CRUD + `POST …/stop`, `…/redeploy`, `…/rollback`, `GET …/health`, `GET …/events` |
| Inference | `POST /deployments/{id}/predict`, `…/predict/raw`, `GET …/inference-logs` |
| Logs | `GET /deployments/{id}/logs` |
| Monitoring | `GET /health`, `GET /ready`, `GET /stats`, per-deployment `…/metrics` and `…/stats` |
| Analytics | `GET /analytics/usage`, `GET /analytics/trends` |
| Metrics | `GET /metrics` (Prometheus, unauthenticated) |

Authentication: JWT from `/auth/login` or API key (`apk_…`) via `Authorization: Bearer`.

## Observability

- **Request tracing:** `X-Request-ID` on every response; included in structured error bodies.
- **HTTP metrics:** `ai_platform_http_requests_total`, `ai_platform_http_request_duration_seconds`.
- **Inference metrics:** `ai_platform_inference_requests_total`, `ai_platform_inference_request_duration_seconds`.
- **Prometheus:** scrapes backend `/metrics` and inference containers discovered via file_sd.

## Known Limitations

- Deployments support **sklearn** models only (onnx/pytorch images exist but are not wired).
- Image build runs synchronously during deploy (may take 30–60 seconds).
- Requires Docker socket access from the backend container.
- Inference logs have no retention/TTL policy yet.

## Implementation Phases

| Phase | Status |
|-------|--------|
| Auth + model upload | Done |
| Deployment engine + sklearn inference | Done |
| Predict proxy + playground UI | Done |
| Logs + health monitoring + API keys | Done |
| Metrics, analytics, nginx gateway | Done |
| Prometheus + Grafana | Done |
| ONNX + PyTorch deployments | Planned |
