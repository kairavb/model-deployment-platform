from pydantic import BaseModel


class LogsResponse(BaseModel):
    deployment_id: str
    tail: int
    logs: str
