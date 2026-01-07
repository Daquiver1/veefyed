"""Image Analysis Service."""

import secrets

from src.enums.skin import SkinIssue, SkinType
from src.models.image_analysis import ImageAnalysisCreate


class ImageAnalysisService:
    """Service for analyzing skin images."""

    @staticmethod
    async def analyze_image(image_id: str, image_path: str) -> ImageAnalysisCreate:
        """Analyze an image and return skin analysis results."""
        return ImageAnalysisService._generate_mock_analysis(image_id, image_path)

    @staticmethod
    def _generate_mock_analysis(image_id: str, image_path: str) -> ImageAnalysisCreate:
        """Generate mock analysis data for development."""
        skin_types = list(SkinType)
        detected_skin_type = secrets.choice(skin_types)

        all_issues = list(SkinIssue)
        num_issues = secrets.randbelow(3) + 1
        detected_issues = secrets.SystemRandom().sample(all_issues, num_issues)

        confidence = round(secrets.SystemRandom().uniform(0.75, 0.98), 2)

        model_version = "v1.0.0-mock"

        return ImageAnalysisCreate(
            image_id=image_id,
            skin_type=detected_skin_type,
            issues=detected_issues,
            confidence_score=confidence,
            model_version=model_version,
        )
