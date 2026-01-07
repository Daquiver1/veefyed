"""Unit tests for repositories."""

from uuid import UUID

import pytest

from src.db.repositories.image import ImageRepository
from src.db.repositories.image_analysis import ImageAnalysisRepository
from src.errors.database import NotFoundError
from src.models.image import ImageCreate
from src.models.image_analysis import ImageAnalysisCreate


class TestImageRepository:
    """Test ImageRepository."""

    @pytest.mark.asyncio
    async def test_create_image(self, mock_db, mock_redis, sample_image_data):
        """Test creating an image."""
        mock_result = {
            **sample_image_data,
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2026-01-07T10:00:00",
            "updated_at": "2026-01-07T10:00:00",
            "is_deleted": False,
        }
        mock_db.fetch_one.return_value = mock_result
        
        repo = ImageRepository(db=mock_db, r_db=mock_redis)
        image_create = ImageCreate(**sample_image_data)
        
        result = await repo.create_image(image_create)
        
        assert str(result.id) == "123e4567-e89b-12d3-a456-426614174000"
        assert result.content_type == "image/jpeg"
        assert result.file_size == 1024000
        mock_db.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_image_found(self, mock_db, mock_redis, sample_image_data):
        """Test getting an existing image."""
        image_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_result = {
            **sample_image_data,
            "id": str(image_id),
            "created_at": "2026-01-07T10:00:00",
            "updated_at": "2026-01-07T10:00:00",
            "is_deleted": False,
        }
        mock_db.fetch_one.return_value = mock_result
        
        repo = ImageRepository(db=mock_db, r_db=mock_redis)
        result = await repo.get_image(image_id)
        
        assert str(result.id) == str(image_id)
        assert result.content_type == "image/jpeg"
        mock_db.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_image_not_found(self, mock_db, mock_redis):
        """Test getting a non-existent image."""
        image_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_db.fetch_one.return_value = None
        
        repo = ImageRepository(db=mock_db, r_db=mock_redis)
        
        with pytest.raises(NotFoundError):
            await repo.get_image(image_id)


class TestImageAnalysisRepository:
    """Test ImageAnalysisRepository."""

    @pytest.mark.asyncio
    async def test_create_analysis(
        self, mock_db, mock_redis, sample_analysis_data
    ):
        """Test creating an analysis."""
        mock_result = {
            **sample_analysis_data,
            "id": "456e4567-e89b-12d3-a456-426614174000",
            "created_at": "2026-01-07T10:00:00",
            "updated_at": "2026-01-07T10:00:00",
            "is_deleted": False,
        }
        mock_db.fetch_one.return_value = mock_result
        
        repo = ImageAnalysisRepository(db=mock_db, r_db=mock_redis)
        analysis_create = ImageAnalysisCreate(**sample_analysis_data)
        
        result = await repo.create_analysis(analysis_create)
        
        assert str(result.id) == "456e4567-e89b-12d3-a456-426614174000"
        assert result.image_id == sample_analysis_data["image_id"]
        assert result.skin_type == "Oily"
        mock_db.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_latest_analysis_found(
        self, mock_db, mock_redis, sample_analysis_data
    ):
        """Test getting latest analysis for an image."""
        image_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_result = {
            **sample_analysis_data,
            "id": "456e4567-e89b-12d3-a456-426614174000",
            "created_at": "2026-01-07T10:00:00",
            "updated_at": "2026-01-07T10:00:00",
            "is_deleted": False,
        }
        mock_db.fetch_one.return_value = mock_result
        
        repo = ImageAnalysisRepository(db=mock_db, r_db=mock_redis)
        result = await repo.get_latest_analysis(image_id)
        
        assert result is not None
        assert result.image_id == str(image_id)
        mock_db.fetch_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_latest_analysis_not_found(self, mock_db, mock_redis):
        """Test getting latest analysis when none exists raises NotFoundError."""
        from src.errors.database import NotFoundError
        
        image_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_db.fetch_one.return_value = None
        
        repo = ImageAnalysisRepository(db=mock_db, r_db=mock_redis)
        
        with pytest.raises(NotFoundError):
            await repo.get_latest_analysis(image_id)
