"""Api Key Scopes Enum."""

from enum import Enum


class ApiKeyScope(str, Enum):
    """API Key Scopes Enum."""

    upload = "upload"
    analyze = "analyze"
