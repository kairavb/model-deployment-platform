import shutil
from pathlib import Path

SKLEARN_SERVER = '''\
import os
import pickle

import numpy as np
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Sklearn Inference Server")
model = None


@app.on_event("startup")
def load_model() -> None:
    global model
    model_path = os.environ.get("MODEL_PATH", "/model/model.file")
    with open(model_path, "rb") as handle:
        model = pickle.load(handle)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}


@app.post("/predict")
def predict(payload: dict) -> dict:
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    inputs = payload.get("inputs")
    if inputs is None:
        raise HTTPException(status_code=400, detail="Missing 'inputs' field")

    predictions = model.predict(np.array(inputs))
    if hasattr(predictions, "tolist"):
        outputs = predictions.tolist()
    else:
        outputs = list(predictions)
    return {"outputs": outputs}
'''

SKLEARN_DOCKERFILE = """\
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi==0.110.0 uvicorn[standard]==0.27.0 scikit-learn==1.4.2 numpy==1.26.4

COPY model.file /model/model.file
COPY server.py /app/server.py

ENV MODEL_PATH=/model/model.file
EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
"""


def prepare_build_context(
    build_dir: Path,
    model_file_path: str,
    framework: str,
) -> None:
    """Write Dockerfile, server code, and model artifact into a build directory."""
    if framework != "sklearn":
        raise ValueError(f"Tier 0 MVP supports sklearn deployments only, got: {framework}")

    build_dir.mkdir(parents=True, exist_ok=True)

    source = Path(model_file_path)
    if not source.is_file():
        raise FileNotFoundError(f"Model file not found: {model_file_path}")

    shutil.copy2(source, build_dir / "model.file")
    (build_dir / "server.py").write_text(SKLEARN_SERVER, encoding="utf-8")
    (build_dir / "Dockerfile").write_text(SKLEARN_DOCKERFILE, encoding="utf-8")


def image_tag_for_deployment(deployment_id: str) -> str:
    return f"ai-platform/deployment-{deployment_id}:latest"
