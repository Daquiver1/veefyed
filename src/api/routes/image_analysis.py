"""Image analysis routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies.auth import require_api_scope
from src.api.dependencies.database import get_repository
from src.db.repositories.image_analysis import ImageAnalysisRepository
from src.enums.api_key import ApiKeyScope
from src.models.api_key import ApiKeyInDb
from src.models.image_analysis import (
    ImageAnalysisPublic,
)

analysis_router = APIRouter()


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
