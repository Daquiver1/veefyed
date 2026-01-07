"""Image Analysis Repository."""

import json
from uuid import UUID

from databases import Database

from src.errors.database import FailedToCreateEntityError, NotFoundError
from src.db.repositories.base import BaseRepository
from src.decorators.db import (
    handle_get_database_exceptions,
    handle_post_database_exceptions,
)
from src.models.image_analysis import ImageAnalysisCreate, ImageAnalysisInDb
from src.services.third_party.redis_client import RedisClient
from src.utils.helpers import Helpers


class ImageAnalysisRepository(BaseRepository):
    """Repository for image analysis results."""

    def __init__(self, db: Database, r_db: RedisClient) -> None:
        """Initialize repository."""
        super().__init__(db=db, r_db=r_db)

    @handle_post_database_exceptions(
        "ImageAnalysis", already_exists_entity="ImageAnalysis"
    )
    async def create_analysis(self, analysis: ImageAnalysisCreate) -> ImageAnalysisInDb:
        """Create mock AI analysis result."""
        analysis_data = analysis.model_dump()
        id_ = await Helpers.generate_uuid()
        analysis_data["id"] = id_

        issues_list = analysis_data["issues"] 
        analysis_data["issues"] = json.dumps(issues_list)

        CREATE_IMAGE_ANALYSIS_QUERY, values = Helpers.generate_create_query(  # noqa: N806
            table_name="image_analysis", fields=analysis_data
        )
        result = await self.db.fetch_one(CREATE_IMAGE_ANALYSIS_QUERY, values=values)
        if not result:
            raise FailedToCreateEntityError("ImageAnalysis")
        data = dict(result) 

        if isinstance(data["issues"], str):
            data["issues"] = json.loads(data["issues"])
        return ImageAnalysisInDb(**data)  # type: ignore

    @handle_get_database_exceptions("ImageAnalysis")
    async def get_latest_analysis(self, image_id: UUID) -> ImageAnalysisInDb | None:
        """Fetch latest analysis for an image."""
        conditions = {"image_id": str(image_id), "is_deleted": False}
        GET_ANALYSIS_QUERY, values = Helpers.generate_select_query(  # noqa: N806
            table_name="image_analysis",
            conditions=conditions,
            order_by="created_at DESC",
            limit=1,
        )
        result = await self.db.fetch_one(GET_ANALYSIS_QUERY, values=values)
        if not result:
            raise NotFoundError("ImageAnalysis", str(image_id))
        data = dict(result) 

        if isinstance(data["issues"], str):
            data["issues"] = json.loads(data["issues"])
        return ImageAnalysisInDb(**data) if result else None  # type: ignore
