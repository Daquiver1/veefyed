"""API key routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import get_api_key
from src.api.dependencies.database import get_repository
from src.db.repositories.api_key import ApiKeyRepository
from src.models.api_key import ApiKeyCreate, ApiKeyInDb, ApiKeyPublic

api_key_router = APIRouter()


@api_key_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create API key",
    description="Create a new API key for a client.",
)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    api_key_repo: Annotated[
        ApiKeyRepository, Depends(get_repository(ApiKeyRepository))
    ],
) -> dict[str, str]:
    """Create API key."""
    key = await api_key_repo.create_api_key(api_key_data)
    return {
        "api_key": key,
        "message": "Store this API key securely; it will not be shown again.",
    }


@api_key_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current API key",
    description="Retrieve metadata for the current API key.",
)
async def get_current_api_key(
    api_key: Annotated[ApiKeyInDb, Depends(get_api_key)],
) -> ApiKeyPublic:
    """Fetch current API key metadata."""
    return api_key


@api_key_router.get(
    "/{api_key}",
    status_code=status.HTTP_200_OK,
    summary="Get API key",
    description="Retrieve API key metadata .",
)
async def get_the_api_key(
    api_key: str,
    api_key_repo: Annotated[
        ApiKeyRepository, Depends(get_repository(ApiKeyRepository))
    ],
) -> ApiKeyPublic:
    """Fetch API key metadata."""
    return await api_key_repo.get_active_api_key(api_key)
