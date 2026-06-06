from uuid import UUID

import httpx
from deployment_engine import IDeploymentEngine

from app.modules.deployments.repository import DeploymentRepository
from app.modules.inference.schemas import PredictRequest, PredictResponse, RawPredictResponse


class InferenceProxy:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client or httpx.AsyncClient(timeout=30.0)

    async def forward_predict(self, internal_url: str, payload: PredictRequest) -> PredictResponse:
        raise NotImplementedError("Inference proxy not implemented yet.")

    async def forward_raw(self, internal_url: str, body: dict) -> RawPredictResponse:
        raise NotImplementedError("Raw inference proxy not implemented yet.")


class InferenceService:
    def __init__(
        self,
        deployment_repository: DeploymentRepository,
        deployment_engine: IDeploymentEngine,
        proxy: InferenceProxy | None = None,
    ) -> None:
        self.deployment_repository = deployment_repository
        self.deployment_engine = deployment_engine
        self.proxy = proxy or InferenceProxy()

    async def predict(
        self,
        user_id: UUID,
        deployment_id: UUID,
        payload: PredictRequest,
    ) -> PredictResponse:
        raise NotImplementedError("Prediction not implemented yet.")

    async def predict_raw(
        self,
        user_id: UUID,
        deployment_id: UUID,
        body: dict,
    ) -> RawPredictResponse:
        raise NotImplementedError("Raw prediction not implemented yet.")
