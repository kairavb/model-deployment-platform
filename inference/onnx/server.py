from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

app = FastAPI(title="ONNX Inference Server")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/info")
def info() -> dict[str, str]:
    return {"framework": "onnx", "status": "not_implemented"}


@app.post("/predict")
def predict(payload: dict) -> dict:
    raise NotImplementedError("Prediction logic not implemented yet.")


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
