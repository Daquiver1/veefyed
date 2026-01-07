"""Formatters module."""

import re


class Formatters:
    """Formatters class"""

    @staticmethod
    def replace_whitespace_with_underscore(text: str) -> str:
        """Remove special characters from a string."""
        return re.sub(r"\s+", "_", text)
