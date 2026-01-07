"""Dependency for db."""

# Standard library imports
from collections.abc import Callable

from databases import Database

# Third party imports
from fastapi import Depends, HTTPException
from starlette.requests import Request

from src.db.repositories.base import BaseRepository
from src.services.third_party.redis_client import RedisClient


def get_database(request: Request) -> Database:
    """Get Postgresql database from app state."""
    return request.app.state._db


def get_redis(request: Request) -> RedisClient:
    """Get Redis client from app state."""
    redis_client = request.app.state._redis_client
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis client not initialized")
    return redis_client


def get_repository(repo_type: type[BaseRepository] | BaseRepository) -> Callable:
    """Dependency for db."""

    def get_repo(
        db: Database = Depends(get_database),  # noqa: B008
        r_db: RedisClient = Depends(get_redis),  # noqa: B008
    ) -> type[BaseRepository]:
        return repo_type(db, r_db)  # type: ignore

    return get_repo
