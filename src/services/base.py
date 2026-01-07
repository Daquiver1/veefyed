"""Base Service."""

from src.db.repositories.base import BaseRepository


class BaseService:
    """Base Service."""

    def __init__(self, repository: BaseRepository) -> None:
        """Initialize with repository instance."""
        self.repository = repository
