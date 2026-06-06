from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.session import engine
from app.modules.auth.router import router as auth_router
from app.modules.deployments.router import router as deployments_router
from app.modules.inference.router import router as inference_router
from app.modules.logs.router import router as logs_router
from app.modules.models.router import router as models_router
from app.modules.monitoring.router import router as monitoring_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(monitoring_router, prefix="/api/v1", tags=["monitoring"])
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
    app.include_router(models_router, prefix="/api/v1", tags=["models"])
    app.include_router(deployments_router, prefix="/api/v1", tags=["deployments"])
    app.include_router(inference_router, prefix="/api/v1", tags=["inference"])
    app.include_router(logs_router, prefix="/api/v1", tags=["logs"])

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return app


app = create_app()


@app.on_event("startup")
async def startup() -> None:
    # Database connectivity is validated lazily by request handlers and migrations.
    _ = engine


@app.on_event("shutdown")
async def shutdown() -> None:
    await engine.dispose()
