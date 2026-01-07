"""Formatters module."""

import datetime
import re
import secrets
from pathlib import Path
from urllib.parse import urlparse

from fastapi import UploadFile

from src.core.config import S3_BUCKET_NAME


class Formatters:
    """Formatters class"""

    @staticmethod
    def extract_object_key_from_url(url: str) -> str:
        """Extract the object key from a standard S3 URL."""
        try:
            parsed_url = urlparse(url)
            if (
                "s3.amazonaws.com" not in parsed_url.netloc
                and "s3." not in parsed_url.netloc
            ):
                raise ValueError("URL is not a valid S3 URL.")

            object_key = parsed_url.path.lstrip("/")

            bucket_name_in_url = parsed_url.netloc.split(".")[0]
            if bucket_name_in_url != S3_BUCKET_NAME:
                raise ValueError(
                    f"URL bucket name '{bucket_name_in_url}' does not match configured bucket name '{S3_BUCKET_NAME}'."
                )

            return object_key
        except Exception as e:
            print(f"Error extracting object key from URL: {e}")
            raise

    @staticmethod
    def format_database_url(db_url: str) -> str:
        """Removes '+asyncpg' from the database URL if present."""
        if "+asyncpg" in db_url:
            modified_url = db_url.replace("+asyncpg", "")
            return modified_url
        # Return the original URL if '+asyncpg' is not found
        return db_url

    @staticmethod
    def format_image_file(file: UploadFile) -> str:
        """Format an image file name."""
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        unique_id = secrets.token_hex(2)
        file_extension = Path(file.filename or "").suffix
        new_file_name = f"{current_date}{unique_id}{file_extension}"
        return new_file_name

    @staticmethod
    def replace_whitespace_with_underscore(text: str) -> str:
        """Remove special characters from a string."""
        return re.sub(r"\s+", "_", text)
