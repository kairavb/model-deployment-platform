import logging
import time
from uuid import UUID

import httpx

from app.core.exceptions import AppError
from app.core.metrics import INFERENCE_LATENCY, INFERENCE_REQUESTS
from app.models.deployment import DeploymentStatus
from app.models.inference_log import InferenceLog
from app.modules.deployments.repository import DeploymentRepository
from app.modules.inference.repository import InferenceLogRepository
from app.modules.inference.schemas import (
    PredictRequest,
    PredictResponse,
    RawPredictResponse,
)

logger = logging.getLogger(__name__)


class InferenceProxy:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client or httpx.AsyncClient(timeout=30.0)

    async def forward_predict(self, internal_url: str, payload: PredictRequest) -> PredictResponse:
        url = f"{internal_url.rstrip('/')}/predict"
        response = await self.client.post(url, json=payload.model_dump())
        response.raise_for_status()
        data = response.json()
        return PredictResponse(outputs=data.get("outputs", []))

    async def forward_raw(self, internal_url: str, body: dict) -> RawPredictResponse:
        url = f"{internal_url.rstrip('/')}/predict"
        response = await self.client.post(url, json=body)
        try:
            parsed = response.json()
        except ValueError:
            parsed = response.text
        return RawPredictResponse(status_code=response.status_code, body=parsed)


class InferenceService:
    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        log_repository: InferenceLogRepository,
        proxy: InferenceProxy | None = None,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.log_repository = log_repository
        self.proxy = proxy or InferenceProxy()

    async def predict(
        self,
        user_id: UUID,
        deployment_id: UUID,
        payload: PredictRequest,
    ) -> PredictResponse:
        deployment = await self._get_running_deployment(user_id, deployment_id)
        assert deployment.internal_url is not None

        start = time.perf_counter()
        status_code = 200
        error_message: str | None = None
        try:
            result = await self.proxy.forward_predict(deployment.internal_url, payload)
            logger.info("Prediction served for deployment %s", deployment_id)
            return result
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            error_message = str(exc)
            logger.error("Prediction failed for deployment %s: %s", deployment_id, exc)
            raise AppError("Inference request failed.", "INFERENCE_ERROR", 502) from exc
        except httpx.HTTPError as exc:
            status_code = 502
            error_message = str(exc)
            logger.error("Prediction failed for deployment %s: %s", deployment_id, exc)
            raise AppError("Inference request failed.", "INFERENCE_ERROR", 502) from exc
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            self._record_metrics(status_code, latency_ms)
            await self._record_log(deployment_id, status_code, latency_ms, error_message)

    async def predict_raw(
        self,
        user_id: UUID,
        deployment_id: UUID,
        body: dict,
    ) -> RawPredictResponse:
        deployment = await self._get_running_deployment(user_id, deployment_id)
        assert deployment.internal_url is not None

        start = time.perf_counter()
        status_code = 200
        error_message: str | None = None
        try:
            result = await self.proxy.forward_raw(deployment.internal_url, body)
            status_code = result.status_code
            if status_code >= 400:
                error_message = f"Upstream returned {status_code}"
            return result
        except httpx.HTTPError as exc:
            status_code = 502
            error_message = str(exc)
            raise AppError("Inference request failed.", "INFERENCE_ERROR", 502) from exc
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            self._record_metrics(status_code, latency_ms)
            await self._record_log(deployment_id, status_code, latency_ms, error_message)

    def _record_metrics(self, status_code: int, latency_ms: float) -> None:
        status = "error" if status_code >= 400 else "success"
        INFERENCE_REQUESTS.labels(status=status).inc()
        INFERENCE_LATENCY.observe(latency_ms / 1000)

    async def list_inference_logs(
        self,
        user_id: UUID,
        deployment_id: UUID,
        limit: int,
    ) -> list[InferenceLog]:
        deployment = await self.deployment_repository.get_by_id(deployment_id, user_id)
        if deployment is None:
            raise AppError("Deployment not found.", "DEPLOYMENT_NOT_FOUND", 404)
        return await self.log_repository.list_by_deployment(deployment_id, limit)

    async def _record_log(
        self,
        deployment_id: UUID,
        status_code: int,
        latency_ms: float,
        error_message: str | None,
    ) -> None:
        await self.log_repository.create(
            InferenceLog(
                deployment_id=deployment_id,
                status_code=status_code,
                latency_ms=latency_ms,
                error_message=error_message,
            )
        )

    async def _get_running_deployment(self, user_id: UUID, deployment_id: UUID):
        deployment = await self.deployment_repository.get_by_id(deployment_id, user_id)
        if deployment is None:
            raise AppError("Deployment not found.", "DEPLOYMENT_NOT_FOUND", 404)
        if deployment.status != DeploymentStatus.RUNNING:
            raise AppError("Deployment is not running.", "DEPLOYMENT_NOT_RUNNING", 409)
        if deployment.internal_url is None:
            raise AppError("Deployment endpoint is not available.", "ENDPOINT_UNAVAILABLE", 409)
        return deployment
