"""Base Repository."""

from databases import Database

from src.services.third_party.redis_client import RedisClient


class BaseRepository:
    """Base class for Postgres repositories."""

    def __init__(self, db: Database, r_db: RedisClient) -> None:
        """Initialize with Postgres database instance."""
        self.db = db
        self.r_db = r_db
