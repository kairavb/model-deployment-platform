from pathlib import Path

from app.models.model import ModelFramework

ALLOWED_EXTENSIONS: dict[ModelFramework, set[str]] = {
    ModelFramework.SKLEARN: {".pkl", ".joblib"},
    ModelFramework.ONNX: {".onnx"},
    ModelFramework.PYTORCH: {".pt", ".pth"},
}


def validate_model_file(framework: ModelFramework, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    allowed = ALLOWED_EXTENSIONS.get(framework, set())
    if suffix not in allowed:
        allowed_list = ", ".join(sorted(allowed))
        raise ValueError(
            f"Invalid file type '{suffix}' for {framework.value}. Allowed: {allowed_list}"
        )
    return suffix
