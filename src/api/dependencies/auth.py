"""Dependency for authentication."""

import logging

from databases import Database
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.api.dependencies.database import get_database, get_redis
from src.db.repositories.api_key import ApiKeyRepository
from src.enums.api_key import ApiKeyScope
from src.models.api_key import ApiKeyInDb
from src.services.third_party.redis_client import RedisClient

app_logger = logging.getLogger("app")


API_KEY_HEADER = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


async def get_api_key_repository(
    db: Database = Depends(get_database),  # noqa: B008
    r_db: RedisClient = Depends(get_redis),  # noqa: B008
) -> ApiKeyRepository:
    """Get API key repository."""
    return ApiKeyRepository(db, r_db)


async def get_api_key(
    api_key: str = Security(API_KEY_HEADER),
    repo: ApiKeyRepository = Depends(get_api_key_repository),  # noqa: B008
) -> ApiKeyInDb:
    """Authenticate API client via API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing",
        )

    key = await repo.get_active_api_key(api_key)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    return key


def require_api_scope(required_scope: ApiKeyScope) -> callable:  # type: ignore
    """Require an API key to have a specific scope."""

    async def wrapper(
        api_key: ApiKeyInDb = Depends(get_api_key),  # noqa: B008
    ) -> ApiKeyInDb:
        if required_scope not in api_key.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {required_scope}",
            )
        return api_key

    return wrapper
