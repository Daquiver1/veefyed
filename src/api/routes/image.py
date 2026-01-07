"""Image routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, status

from src.api.dependencies.auth import require_api_scope
from src.api.dependencies.database import get_repository
from src.db.repositories.image import ImageRepository
from src.enums.api_key import ApiKeyScope
from src.models.api_key import ApiKeyInDb
from src.models.image import ImageCreate, ImagePublic

image_router = APIRouter()


@image_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Upload image",
    description="Upload an image and persist metadata. Requires upload scope.",
)
async def upload_image(
    image: UploadFile,
    image_repo: Annotated[ImageRepository, Depends(get_repository(ImageRepository))],
    # api_key: Annotated[ApiKeyInDb, Depends(require_api_scope(ApiKeyScope.upload))],
) -> ImagePublic:
    """Upload image metadata."""
    
    return await image_repo.create_image(image_data)


@image_router.get(
    "/{image_id}",
    status_code=status.HTTP_200_OK,
    summary="Get image metadata",
    description="Retrieve stored image metadata by ID.",
)
async def get_image(
    image_id: UUID,
    image_repo: Annotated[ImageRepository, Depends(get_repository(ImageRepository))],
    api_key: Annotated[ApiKeyInDb, Depends(require_api_scope(ApiKeyScope.upload))],
) -> ImagePublic | None:
    """Fetch image metadata."""
    return await image_repo.get_image(image_id)
