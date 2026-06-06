from enum import Enum


class DeploymentState(str, Enum):
    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


ALLOWED_TRANSITIONS: dict[DeploymentState, set[DeploymentState]] = {
    DeploymentState.PENDING: {DeploymentState.STARTING, DeploymentState.FAILED},
    DeploymentState.STARTING: {DeploymentState.RUNNING, DeploymentState.FAILED},
    DeploymentState.RUNNING: {DeploymentState.STOPPING, DeploymentState.FAILED},
    DeploymentState.STOPPING: {DeploymentState.STOPPED, DeploymentState.FAILED},
    DeploymentState.STOPPED: {DeploymentState.STARTING},
    DeploymentState.FAILED: {DeploymentState.STOPPED},
}


def can_transition(current: DeploymentState, next_state: DeploymentState) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    return next_state in allowed
