from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
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
    max_upload_size_mb: int = 500

    docker_network: str = "ai-platform-net"
    inference_host_port_min: int = 9000
    inference_host_port_max: int = 9999
    max_deployments_per_user: int = 5
    deployment_health_timeout_seconds: int = 60

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


settings = Settings()
