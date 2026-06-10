from app.core.exceptions import AppError
from app.models.deployment import DeploymentStatus

ALLOWED_TRANSITIONS: dict[DeploymentStatus, set[DeploymentStatus]] = {
    DeploymentStatus.PENDING: {DeploymentStatus.STARTING, DeploymentStatus.FAILED},
    DeploymentStatus.STARTING: {DeploymentStatus.RUNNING, DeploymentStatus.FAILED},
    DeploymentStatus.RUNNING: {
        DeploymentStatus.STOPPING,
        DeploymentStatus.STARTING,
        DeploymentStatus.FAILED,
    },
    DeploymentStatus.STOPPING: {DeploymentStatus.STOPPED, DeploymentStatus.FAILED},
    DeploymentStatus.STOPPED: {DeploymentStatus.STARTING},
    DeploymentStatus.FAILED: {DeploymentStatus.STOPPING, DeploymentStatus.STARTING},
}

REDEPLOYABLE_STATUSES = (
    DeploymentStatus.RUNNING,
    DeploymentStatus.STOPPED,
    DeploymentStatus.FAILED,
)


def ensure_transition(current: DeploymentStatus, next_state: DeploymentStatus) -> None:
    if next_state not in ALLOWED_TRANSITIONS.get(current, set()):
        raise AppError(
            f"Invalid deployment transition from {current.value} to {next_state.value}.",
            "INVALID_DEPLOYMENT_TRANSITION",
            409,
        )
