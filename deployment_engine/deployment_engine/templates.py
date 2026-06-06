from dataclasses import dataclass


@dataclass(frozen=True)
class InferenceImageConfig:
    framework: str
    image: str
    model_mount_path: str = "/model/model.file"
    internal_port: int = 8080


def get_inference_image_config(framework: str, images: dict[str, str]) -> InferenceImageConfig:
    """Resolve the inference image configuration for a framework."""
    image = images.get(framework)
    if image is None:
        raise ValueError(f"Unsupported framework: {framework}")

    return InferenceImageConfig(
        framework=framework,
        image=image,
    )


def build_container_name(deployment_id: str) -> str:
    """Build a deterministic container name for a deployment."""
    return f"inference-{deployment_id}"
