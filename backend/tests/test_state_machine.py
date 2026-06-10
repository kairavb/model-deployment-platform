import pytest

from app.core.exceptions import AppError
from app.models.deployment import DeploymentStatus
from app.modules.deployments.state_machine import ensure_transition


def test_valid_transitions() -> None:
    ensure_transition(DeploymentStatus.PENDING, DeploymentStatus.STARTING)
    ensure_transition(DeploymentStatus.STARTING, DeploymentStatus.RUNNING)
    ensure_transition(DeploymentStatus.RUNNING, DeploymentStatus.STOPPING)
    ensure_transition(DeploymentStatus.RUNNING, DeploymentStatus.STARTING)
    ensure_transition(DeploymentStatus.FAILED, DeploymentStatus.STARTING)


def test_invalid_transitions() -> None:
    with pytest.raises(AppError, match="Invalid deployment transition"):
        ensure_transition(DeploymentStatus.PENDING, DeploymentStatus.RUNNING)
    with pytest.raises(AppError, match="Invalid deployment transition"):
        ensure_transition(DeploymentStatus.STOPPED, DeploymentStatus.RUNNING)
