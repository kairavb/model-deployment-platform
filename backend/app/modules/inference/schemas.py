from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    inputs: list[Any] = Field(default_factory=list)


class PredictResponse(BaseModel):
    outputs: list[Any] = Field(default_factory=list)


class RawPredictResponse(BaseModel):
    status_code: int
    body: dict[str, Any] | list[Any] | str
