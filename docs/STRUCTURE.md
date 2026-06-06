# Repository Structure

## Backend (`backend/app/`)

```
app/
├── main.py                 # FastAPI app factory and router registration
├── config.py               # Environment settings
├── dependencies.py         # Shared FastAPI dependencies
├── core/                   # Security and exception helpers
├── db/                     # SQLAlchemy base and session
├── models/                 # SQLAlchemy ORM entities
└── modules/
    ├── auth/
    ├── models/
    ├── deployments/
    ├── inference/
    ├── logs/
    └── monitoring/
```

Each module follows the same shape:

```
module/
├── router.py       # HTTP routes
├── service.py      # Business orchestration (stubs)
├── repository.py   # Database access
└── schemas.py      # Pydantic request/response models
```

## Deployment Engine (`deployment_engine/deployment_engine/`)

```
deployment_engine/
├── interface.py        # IDeploymentEngine protocol
├── models.py           # DeploymentSpec, DeploymentResult, ContainerStatus
├── docker_engine.py    # Docker SDK implementation (stubs)
├── templates.py        # Image and container naming helpers
└── health_checker.py   # HTTP health probing
```

## Frontend (`frontend/src/`)

```
src/
├── api/                # Typed API clients
├── components/         # Layout and UI primitives
├── pages/              # Route-level screens
├── hooks/              # Shared React hooks
├── types/              # TypeScript interfaces
└── utils/              # Formatting helpers
```

## Conventions

- Route handlers stay thin and delegate to services.
- Services raise `NotImplementedError` until business logic is added.
- Repositories contain SQLAlchemy queries only.
- Schemas are separate from ORM models.
- The deployment engine never exposes HTTP routes directly.
