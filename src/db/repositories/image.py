"""Review Repository."""

from uuid import UUID

from databases import Database

from src.db.repositories.base import BaseRepository
from src.decorators.db import (
    handle_get_database_exceptions,
    handle_post_database_exceptions,
)
from src.errors.database import NotFoundError
from src.models.image import ImageCreate, ImageInDb
from src.services.third_party.redis_client import RedisClient
from src.utils.helpers import Helpers


class ImageRepository(BaseRepository):
    """Repository for image storage and retrieval."""

    def __init__(self, db: Database, r_db: RedisClient) -> None:
        """Initialize repository."""
        super().__init__(db=db, r_db=r_db)

    @handle_post_database_exceptions("Image", already_exists_entity="Image")
    async def create_image(self, image: ImageCreate) -> ImageInDb:
        """Persist uploaded image metadata."""
        image_data = image.model_dump()
        id_ = await Helpers.generate_uuid()
        image_data["id"] = id_

        CREATE_IMAGE_QUERY, values = Helpers.generate_create_query(  # noqa: N806
            table_name="images", fields=image_data
        )

        result = await self.db.fetch_one(CREATE_IMAGE_QUERY, values=values)
        return ImageInDb(**result)  # type: ignore

    @handle_get_database_exceptions("Image")
    async def get_image(self, image_id: UUID) -> ImageInDb | None:
        """Fetch image by ID."""
        conditions = {"id": str(image_id), "is_deleted": False}
        GET_IMAGE_BY_ID_QUERY, values = Helpers.generate_select_query(  # noqa: N806
            table_name="images",
            conditions=conditions,
        )
        result = await self.db.fetch_one(GET_IMAGE_BY_ID_QUERY, values=values)
        if not result:
            raise NotFoundError("image", str(image_id))
        return ImageInDb(**result)  # type: ignore
