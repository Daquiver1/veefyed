"""Image routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.api.dependencies.auth import require_api_scope
from src.api.dependencies.database import get_repository
from src.db.repositories.image import ImageRepository
from src.enums.api_key import ApiKeyScope
from src.models.api_key import ApiKeyInDb
from src.models.image import ImageCreate, ImagePublic
from src.utils.helpers import Helpers

image_router = APIRouter()


@image_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Upload image",
    description="Upload an image and persist metadata. Requires upload scope.",
)
async def upload_image(
    image: Annotated[UploadFile, File(description="Image file to upload")],
    image_repo: Annotated[ImageRepository, Depends(get_repository(ImageRepository))],
    api_key: Annotated[ApiKeyInDb, Depends(require_api_scope(ApiKeyScope.upload))],
) -> ImagePublic:
    """Upload image metadata."""
    file_size, storage_path = await Helpers.save_uploaded_file(
        file=image,
        allowed_types=["image/jpeg", "image/png"],
        max_size_mb=5,
    )

    image_data = ImageCreate(
        content_type=image.content_type,
        file_size=file_size,
        storage_path=storage_path,
    )
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
