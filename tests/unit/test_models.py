"""Unit tests for models."""

import pytest
from pydantic import ValidationError

from src.enums.skin import SkinIssue, SkinType
from src.models.image import ImageCreate, ImagePublic
from src.models.image_analysis import ImageAnalysisCreate, ImageAnalysisPublic


class TestImageModels:
    """Test Image models."""

    def test_image_create_valid(self, sample_image_data):
        """Test creating valid ImageCreate model."""
        image = ImageCreate(**sample_image_data)
        assert image.content_type == "image/jpeg"
        assert image.file_size == 1024000
        assert image.storage_path == "/uploads/images/test-image.jpg"

    def test_image_create_missing_fields(self):
        """Test ImageCreate with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ImageCreate(content_type="image/jpeg")
        assert "file_size" in str(exc_info.value)
        assert "storage_path" in str(exc_info.value)

    def test_image_create_invalid_type(self):
        """Test ImageCreate with invalid field types."""
        with pytest.raises(ValidationError):
            ImageCreate(
                content_type="image/jpeg",
                file_size="invalid",  # Should be int
                storage_path="/path/to/image.jpg",
            )

    def test_image_public_includes_mixins(self, sample_image_data):
        """Test ImagePublic includes UUID and DateTime fields."""
        image_data = {
            **sample_image_data,
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2026-01-07T10:00:00",
            "updated_at": "2026-01-07T10:00:00",
        }
        image = ImagePublic(**image_data)
        assert str(image.id) == "123e4567-e89b-12d3-a456-426614174000"
        assert image.created_at is not None
        assert image.updated_at is not None


class TestImageAnalysisModels:
    """Test ImageAnalysis models."""

    def test_image_analysis_create_valid(self, sample_analysis_data):
        """Test creating valid ImageAnalysisCreate model."""
        analysis = ImageAnalysisCreate(**sample_analysis_data)
        assert analysis.image_id == "123e4567-e89b-12d3-a456-426614174000"
        assert analysis.skin_type == SkinType.oily
        assert SkinIssue.acne in analysis.issues
        assert analysis.confidence_score == 0.92
        assert analysis.model_version == "v1.0.0-mock"

    def test_image_analysis_create_missing_fields(self):
        """Test ImageAnalysisCreate with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ImageAnalysisCreate(
                image_id="123e4567-e89b-12d3-a456-426614174000",
                skin_type=SkinType.oily,
            )
        assert "issues" in str(exc_info.value)

    def test_image_analysis_invalid_skin_type(self, sample_analysis_data):
        """Test ImageAnalysisCreate with invalid skin type."""
        sample_analysis_data["skin_type"] = "InvalidType"
        with pytest.raises(ValidationError):
            ImageAnalysisCreate(**sample_analysis_data)

    def test_image_analysis_invalid_issue(self, sample_analysis_data):
        """Test ImageAnalysisCreate with invalid issue."""
        sample_analysis_data["issues"] = ["InvalidIssue"]
        with pytest.raises(ValidationError):
            ImageAnalysisCreate(**sample_analysis_data)

    def test_image_analysis_confidence_range(self, sample_analysis_data):
        """Test ImageAnalysisCreate accepts valid confidence scores."""
        # Valid scores
        for score in [0.0, 0.5, 0.99, 1.0]:
            data = {**sample_analysis_data, "confidence_score": score}
            analysis = ImageAnalysisCreate(**data)
            assert analysis.confidence_score == score

    def test_image_analysis_public_includes_mixins(self, sample_analysis_data):
        """Test ImageAnalysisPublic includes UUID and DateTime fields."""
        analysis_data = {
            **sample_analysis_data,
            "id": "456e4567-e89b-12d3-a456-426614174000",
            "created_at": "2026-01-07T10:00:00",
            "updated_at": "2026-01-07T10:00:00",
        }
        analysis = ImageAnalysisPublic(**analysis_data)
        assert str(analysis.id) == "456e4567-e89b-12d3-a456-426614174000"
        assert analysis.created_at is not None
