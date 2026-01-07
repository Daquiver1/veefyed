"""Image analysis routes."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.auth import require_api_scope
from src.enums.api_key import ApiKeyScope
from src.models.api_key import ApiKeyInDb
from src.api.dependencies.database import get_repository
from src.db.repositories.image import ImageRepository
from src.db.repositories.image_analysis import ImageAnalysisRepository
from src.models.image_analysis import ImageAnalysisPublic
from src.services.image_analysis_service import ImageAnalysisService

analysis_router = APIRouter()

app_logger = logging.getLogger("app")

@analysis_router.post(
    "/{image_id}/analyze",
    status_code=status.HTTP_201_CREATED,
    summary="Create image analysis",
    description="Analyze an image and return skin analysis results. Requires analyze scope.",
)
async def create_image_analysis(
    image_id: UUID,
    image_repo: Annotated[ImageRepository, Depends(get_repository(ImageRepository))],
    analysis_repo: Annotated[
        ImageAnalysisRepository, Depends(get_repository(ImageAnalysisRepository))
    ],
    api_key: Annotated[ApiKeyInDb, Depends(require_api_scope(ApiKeyScope.analyze))],
) -> ImageAnalysisPublic:
    """Create a new image analysis."""
    image = await image_repo.get_image(image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    analysis_data = await ImageAnalysisService.analyze_image(
        image_id=str(image_id),
        image_path=image.storage_path,
    )

    analysis = await analysis_repo.create_analysis(analysis_data)

    return analysis


@analysis_router.get(
    "/{image_id}/analysis",
    status_code=status.HTTP_200_OK,
    summary="Get latest analysis",
    description="Retrieve latest analysis result for an image.",
)
async def get_latest_analysis(
    image_id: UUID,
    analysis_repo: Annotated[
        ImageAnalysisRepository, Depends(get_repository(ImageAnalysisRepository))
    ],
    api_key: Annotated[ApiKeyInDb, Depends(require_api_scope(ApiKeyScope.analyze))],
) -> ImageAnalysisPublic:
    """Get latest analysis."""
    analysis = await analysis_repo.get_latest_analysis(image_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )
    return analysis
