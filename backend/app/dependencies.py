from collections.abc import AsyncGenerator
from functools import lru_cache
from uuid import UUID

from deployment_engine import DockerDeploymentEngine
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import decode_token, hash_api_key, is_api_key
from app.db.session import get_session
from app.models.user import User
from app.modules.auth.api_key_repository import ApiKeyRepository
from app.modules.auth.repository import AuthRepository

security_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    token = credentials.credentials

    if is_api_key(token):
        api_key = await ApiKeyRepository(db).get_active_by_hash(hash_api_key(token))
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked API key.",
            )
        await ApiKeyRepository(db).touch_last_used(api_key)
        user = await AuthRepository(db).get_by_id(api_key.user_id)
    else:
        try:
            user_id = decode_token(token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            ) from None
        user = await AuthRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user


async def get_current_user_id(current_user: User = Depends(get_current_user)) -> UUID:
    return current_user.id


@lru_cache
def get_deployment_engine() -> DockerDeploymentEngine:
    return DockerDeploymentEngine(
        docker_network=settings.docker_network,
        build_base_path=settings.deployment_build_path,
        health_timeout_seconds=settings.deployment_health_timeout_seconds,
        port_min=settings.inference_host_port_min,
        port_max=settings.inference_host_port_max,
    )
