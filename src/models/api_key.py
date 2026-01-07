"""Api Key Model"""

from pydantic import BaseModel

from src.enums.api_key import ApiKeyScope
from src.models.core import DateTimeModelMixin, IsDeletedModelMixin, UUIDModelMixin


class ApiKeyBase(BaseModel):
    """API Key base model."""

    name: str
    scopes: list[ApiKeyScope]


class ApiKeyCreate(ApiKeyBase):
    """API Key creation model."""

    pass


class ApiKeyPublic(ApiKeyBase, DateTimeModelMixin, UUIDModelMixin):
    """API Key model in DB."""

    is_active: bool


class ApiKeyInDb(ApiKeyPublic, IsDeletedModelMixin):
    """API Key model in DB."""

    key_hash: str
    key_prefix: str
