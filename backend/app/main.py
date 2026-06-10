import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_client import make_asgi_app

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.health_monitor import run_health_monitor
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.db.session import SessionLocal, engine
from app.dependencies import get_deployment_engine
from app.modules.analytics.router import router as analytics_router
from app.modules.auth.router import router as auth_router
from app.modules.deployments.router import router as deployments_router
from app.modules.inference.router import router as inference_router
from app.modules.logs.router import router as logs_router
from app.modules.models.router import router as models_router
from app.modules.monitoring.router import router as monitoring_router

OPENAPI_TAGS = [
    {"name": "monitoring", "description": "Platform health, readiness, and Prometheus metrics."},
    {"name": "auth", "description": "Registration, login, profile, and API key management."},
    {"name": "models", "description": "Model registry and version uploads."},
    {"name": "deployments", "description": "Deployment lifecycle, health, and events."},
    {"name": "inference", "description": "Authenticated prediction proxy and inference logs."},
    {"name": "logs", "description": "Container log retrieval for deployments."},
    {"name": "analytics", "description": "Usage summaries and request/error trends."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging(settings.debug)
    from app.core.prometheus_targets import sync_inference_targets

    async with SessionLocal() as session:
        await sync_inference_targets(session)

    monitor_task = asyncio.create_task(run_health_monitor(get_deployment_engine))
    yield
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Platform API",
        description=(
            "REST API for the Cloud-Native AI Deployment Platform. "
            "Authenticate with a JWT from `/auth/login` or an API key (`apk_…`) via Bearer token. "
            "Interactive documentation is available at `/docs`."
        ),
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(monitoring_router, prefix="/api/v1", tags=["monitoring"])
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
    app.include_router(models_router, prefix="/api/v1", tags=["models"])
    app.include_router(deployments_router, prefix="/api/v1", tags=["deployments"])
    app.include_router(inference_router, prefix="/api/v1", tags=["inference"])
    app.include_router(logs_router, prefix="/api/v1", tags=["logs"])
    app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    app.openapi = lambda: _custom_openapi(app)

    return app


def _custom_openapi(app: FastAPI) -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
    )
    schema["info"]["contact"] = {
        "name": "AI Platform",
        "url": "https://github.com/ai-platform",
    }
    schema.setdefault("components", {}).setdefault("schemas", {})["ErrorResponse"] = {
        "type": "object",
        "properties": {
            "detail": {"type": "string"},
            "code": {"type": "string"},
            "request_id": {"type": "string"},
            "hint": {"type": "string"},
            "errors": {"type": "array", "items": {"type": "object"}},
        },
        "required": ["detail", "code"],
    }
    app.openapi_schema = schema
    return schema


app = create_app()
