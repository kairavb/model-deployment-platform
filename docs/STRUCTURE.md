# Repository Structure

## Backend (`backend/app/`)

```
app/
├── main.py                 # FastAPI app factory, middleware, lifespan hooks
├── config.py               # Environment settings and startup validation
├── dependencies.py         # Auth, DB session, deployment engine DI
├── core/                   # Cross-cutting concerns
│   ├── security.py         # Password hashing, JWT, API keys
│   ├── exceptions.py       # AppError and global exception handlers
│   ├── middleware.py       # Request ID, logging, HTTP metrics
│   ├── metrics.py          # Prometheus metric definitions
│   ├── health_monitor.py   # Background deployment health probes
│   ├── logging.py          # Structured logging setup
│   └── prometheus_targets.py
├── db/                     # SQLAlchemy base and session
├── models/                 # SQLAlchemy ORM entities
└── modules/
    ├── auth/               # Registration, login, API keys
    ├── models/             # Model registry and uploads
    ├── deployments/        # Lifecycle, events, state machine
    ├── inference/          # Prediction proxy and inference logs
    ├── logs/               # Container log retrieval
    ├── monitoring/         # Health, readiness, per-deployment stats
    └── analytics/          # Usage summaries and trends
```

Each module follows the same shape:

```
module/
├── router.py       # HTTP routes (thin)
├── service.py      # Business orchestration
├── repository.py   # Database access
└── schemas.py      # Pydantic request/response models
```

## Deployment Engine (`deployment_engine/deployment_engine/`)

```
deployment_engine/
├── interface.py            # IDeploymentEngine protocol
├── models.py               # DeploymentSpec, DeploymentResult, ContainerStatus
├── docker_engine.py        # Docker SDK implementation
├── dockerfile_generator.py # Per-deployment image build context
├── templates.py            # Image and container naming helpers
└── health_checker.py       # HTTP health probing
```

## Infrastructure (`infra/`)

```
infra/
├── nginx/              # Reverse proxy for API, docs, and dashboard
├── prometheus/         # Scrape config + inference file_sd targets
└── grafana/            # Datasource and dashboard provisioning
```

## Frontend (`frontend/src/`)

```
src/
├── api/                # Typed API clients (shared fetch wrapper in client.ts)
├── components/         # Layout and UI primitives
├── context/            # React context providers (auth)
├── pages/              # Route-level screens
├── types/              # TypeScript interfaces
└── utils/              # API URL helpers, auth token storage, formatting
```

## Conventions

- Route handlers stay thin and delegate to services.
- Services raise `AppError` for domain failures; unexpected errors bubble to the global handler.
- Repositories contain SQLAlchemy queries only.
- Schemas are separate from ORM models.
- Deployment status changes go through `state_machine.ensure_transition`.
- The deployment engine never exposes HTTP routes directly.
