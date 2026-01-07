"""Review models."""

from pydantic import BaseModel, Field

from src.models.core import DateTimeModelMixin, IsDeletedModelMixin, UUIDModelMixin


class ImageBase(BaseModel):
    """Review base model."""

    filename: str = Field(..., description="Original filename")
    content_type: str
    file_size: int = Field(..., description="Size in bytes")
    storage_path: str = Field(..., description="Local filesystem path")


class ImageCreate(ImageBase):
    """Review creation model."""

    class Config:
        """Model configuration."""

        from_attributes = True
        forbid = True


class ImagePublic(ImageBase, DateTimeModelMixin, UUIDModelMixin):
    """Review public model."""

    pass


class ImageInDb(ImagePublic, IsDeletedModelMixin):
    """Review model as stored in database."""

    pass
