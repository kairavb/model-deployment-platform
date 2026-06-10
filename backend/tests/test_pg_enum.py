from sqlalchemy import select
from sqlalchemy.dialects.postgresql.asyncpg import dialect as asyncpg_dialect

from app.models.deployment import Deployment, DeploymentStatus


def test_deployment_status_filter_uses_enum_value() -> None:
    stmt = select(Deployment).where(Deployment.status == DeploymentStatus.RUNNING)
    compiled = stmt.compile(dialect=asyncpg_dialect())
    param = compiled.params["status_1"]
    assert param is DeploymentStatus.RUNNING
    assert param.value == "running"
