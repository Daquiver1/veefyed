"""API Key Repository."""

import json

from databases import Database

from src.db.repositories.base import BaseRepository
from src.decorators.db import (
    handle_get_database_exceptions,
    handle_post_database_exceptions,
)
from src.errors.database import NotFoundError
from src.models.api_key import ApiKeyCreate, ApiKeyInDb
from src.services.third_party.redis_client import RedisClient
from src.utils.helpers import Helpers


class ApiKeyRepository(BaseRepository):
    """Repository for API key management and authentication."""

    def __init__(self, db: Database, r_db: RedisClient) -> None:
        """Initialize repository."""
        super().__init__(db=db, r_db=r_db)

    @handle_post_database_exceptions("ApiKey", already_exists_entity="ApiKey")
    async def create_api_key(self, api_key: ApiKeyCreate) -> str:
        """Create and persist a new API key."""
        api_key_data = api_key.model_dump()
        api_key_data["id"] = await Helpers.generate_uuid()

        raw_key = Helpers.generate_api_key()
        api_key_data["key_hash"] = Helpers.hash_api_key(raw_key)

        key_prefix = raw_key.split("_")[0] + "_" + raw_key.split("_")[1]
        api_key_data["key_prefix"] = key_prefix

        api_key_data["scopes"] = json.dumps(
            [scope.value for scope in api_key_data["scopes"]]
        )

        CREATE_API_KEY_QUERY, values = Helpers.generate_create_query(  # noqa: N806
            table_name="api_keys",
            fields=api_key_data,
        )

        await self.db.fetch_one(CREATE_API_KEY_QUERY, values=values)
        return raw_key

    @handle_get_database_exceptions("ApiKey")
    async def get_active_api_key(self, raw_key: str) -> ApiKeyInDb:
        """Fetch an active API key by raw key value."""
        try:
            key_prefix = raw_key.split("_")[0] + "_" + raw_key.split("_")[1]
        except IndexError:
            raise NotFoundError("api_key", "invalid_format")  # noqa: B904

        conditions = {
            "key_prefix": key_prefix,
            "is_active": True,
            "is_deleted": False,
        }

        GET_API_KEY_QUERY, values = Helpers.generate_select_query(
            table_name="api_keys",
            conditions=conditions,
        )
        result = await self.db.fetch_one(GET_API_KEY_QUERY, values=values)
        if not result:
            raise NotFoundError("api_key", "provided_key_prefix")

        stored_hash = result["key_hash"]

        if not Helpers.verify_api_key(raw_key, stored_hash):
            raise NotFoundError("api_key", "verification_failed")

        data = dict(result)
        if isinstance(data["scopes"], str):
            try:
                data["scopes"] = json.loads(result["scopes"])
            except json.JSONDecodeError as e:
                raise ValueError(f"Corrupt JSON data in 'scopes' field: {e}")  # noqa: B904
        return ApiKeyInDb(**data)  # type: ignore
