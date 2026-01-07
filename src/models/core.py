"""Core data that exist in all Models."""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator, validator


class CoreModel(BaseModel):
    """Any common logic to be shared by all models."""

    def model_dump(self, **kwargs: Any) -> dict:  # noqa: ANN401
        """Dump model data with JSON serialization of context field."""
        data = super().model_dump(**kwargs)
        if isinstance(data.get("context"), dict):
            data["context"] = json.dumps(data["context"])
        return data

    @field_validator("context", mode="before", check_fields=False)
    @classmethod
    def deserialize_context(cls, v: str | dict) -> dict:
        """Deserialize context from JSON string to dict"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return {}
        return v


class IDModelMixin(BaseModel):
    """ID data."""

    id: int


class DateTimeModelMixin(BaseModel):
    """Datetime model dates."""

    created_at: datetime
    updated_at: datetime | None

    @validator("created_at", "updated_at", pre=True)
    def default_datetime(cls, value: datetime) -> datetime:  # noqa
        """Validate both created_at and update_at data."""
        return value or datetime.now()

    def model_dump(self, *args: Any, **kwargs: Any) -> dict:  # noqa: ANN401
        """Dump model data."""
        d = super().model_dump(*args, **kwargs)
        for field in ["created_at", "updated_at"]:
            if d[field]:
                d[field] = d[field].isoformat()
        return d


class UUIDModelMixin(BaseModel):
    """UUID data."""

    id: UUID


class UserIDModelMixin(BaseModel):
    """User ID data."""

    user_id: UUID


class IsDeletedModelMixin(BaseModel):
    """Is deleted data."""

    is_deleted: bool = False
