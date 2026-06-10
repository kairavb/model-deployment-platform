import pytest

from app.models.model import ModelFramework
from app.modules.models.validators import validate_model_file


def test_validate_sklearn_extensions() -> None:
    assert validate_model_file(ModelFramework.SKLEARN, "model.pkl") == ".pkl"
    assert validate_model_file(ModelFramework.SKLEARN, "model.joblib") == ".joblib"


def test_validate_rejects_invalid_extension() -> None:
    with pytest.raises(ValueError):
        validate_model_file(ModelFramework.SKLEARN, "model.onnx")
