import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_INSECURE_SECRET_KEYS = frozenset({"change-me", "change-me-to-a-random-secret-key"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    app_name: str = "ai-platform"
    app_env: str = "development"
    debug: bool = True

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    cors_origins: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://aiplatform:aiplatform@localhost:5432/aiplatform"

    model_storage_path: str = "./storage/models"
    deployment_build_path: str = "./storage/builds"
    max_upload_size_mb: int = 500

    docker_network: str = "ai-platform-net"
    inference_host_port_min: int = 9000
    inference_host_port_max: int = 9999
    max_deployments_per_user: int = 5
    deployment_health_timeout_seconds: int = 60
    prometheus_targets_path: str = "./storage/prometheus/inference_targets.json"

    inference_image_sklearn: str = "ai-platform/inference-sklearn:latest"
    inference_image_onnx: str = "ai-platform/inference-onnx:latest"
    inference_image_pytorch: str = "ai-platform/inference-pytorch:latest"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def inference_images(self) -> dict[str, str]:
        return {
            "sklearn": self.inference_image_sklearn,
            "onnx": self.inference_image_onnx,
            "pytorch": self.inference_image_pytorch,
        }


def validate_settings(config: Settings) -> None:
    """Fail fast on unsafe production configuration."""
    if config.secret_key in _INSECURE_SECRET_KEYS:
        if config.app_env.lower() in {"production", "prod"}:
            raise RuntimeError(
                "SECRET_KEY must be set to a strong random value when APP_ENV is production."
            )
        logger.warning("Using default SECRET_KEY — set SECRET_KEY in .env before deploying.")


settings = Settings()
validate_settings(settings)
