"""Image analysis models."""

from datetime import datetime

from pydantic import BaseModel

from src.enums.skin import SkinIssue, SkinType
from src.models.core import DateTimeModelMixin, IsDeletedModelMixin, UUIDModelMixin


class ImageAnalysisBase(BaseModel):
    """Base model for image analysis."""

    image_id: str
    skin_type: SkinType
    issues: list[SkinIssue]
    confidence_score: float
    model_ver4555sion: str
    analyzed_at: datetime


class ImageAnalysisCreate(ImageAnalysisBase):
    """Model for creating image analysis."""

    pass


class ImageAnalysisPublic(ImageAnalysisBase, UUIDModelMixin, DateTimeModelMixin):
    """Public model for image analysis."""

    pass


class ImageAnalysisInDb(IsDeletedModelMixin):
    """Model representing image analysis stored in the database."""

    pass
