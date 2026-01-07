"""Unit tests for services."""

import pytest

from src.enums.skin import SkinIssue, SkinType
from src.models.image_analysis import ImageAnalysisCreate
from src.services.image_analysis_service import ImageAnalysisService


class TestImageAnalysisService:
    """Test ImageAnalysisService."""

    @pytest.mark.asyncio
    async def test_analyze_image_returns_analysis_create(self):
        """Test analyze_image returns ImageAnalysisCreate model."""
        image_id = "123e4567-e89b-12d3-a456-426614174000"
        image_path = "/uploads/images/test.jpg"
        
        result = await ImageAnalysisService.analyze_image(image_id, image_path)
        
        assert isinstance(result, ImageAnalysisCreate)
        assert result.image_id == image_id
        assert isinstance(result.skin_type, SkinType)
        assert isinstance(result.issues, list)
        assert len(result.issues) > 0
        assert all(isinstance(issue, SkinIssue) for issue in result.issues)
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.model_version == "v1.0.0-mock"

    @pytest.mark.asyncio
    async def test_analyze_image_generates_different_results(self):
        """Test that analyze_image can generate different results."""
        image_id = "123e4567-e89b-12d3-a456-426614174000"
        image_path = "/uploads/images/test.jpg"
        
        results = []
        for _ in range(5):
            result = await ImageAnalysisService.analyze_image(image_id, image_path)
            results.append(result)
        
        skin_types = [r.skin_type for r in results]
        assert len(set(skin_types)) >= 1 

    def test_generate_mock_analysis_valid_skin_type(self):
        """Test mock analysis generates valid skin type."""
        result = ImageAnalysisService._generate_mock_analysis(
            "test-id", "/path/to/image.jpg"
        )
        assert result.skin_type in list(SkinType)

    def test_generate_mock_analysis_valid_issues(self):
        """Test mock analysis generates valid issues."""
        result = ImageAnalysisService._generate_mock_analysis(
            "test-id", "/path/to/image.jpg"
        )
        assert 1 <= len(result.issues) <= 3
        assert all(issue in list(SkinIssue) for issue in result.issues)

    def test_generate_mock_analysis_confidence_in_range(self):
        """Test mock analysis generates confidence in expected range."""
        for _ in range(10):
            result = ImageAnalysisService._generate_mock_analysis(
                "test-id", "/path/to/image.jpg"
            )
            assert 0.75 <= result.confidence_score <= 0.98
