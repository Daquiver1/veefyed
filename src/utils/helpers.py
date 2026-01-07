"""Helper functions for the project"""

import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

from src.core.config import UPLOAD_DIR
from src.errors.core import CustomizedValueError

app_logger = logging.getLogger("app")


class Helpers:
    """Helpers class"""

    @staticmethod
    async def generate_uuid() -> str:
        """Generate uuid for user id."""
        return str(uuid.uuid4())

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash the API key using a secure hashing algorithm."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def generate_select_query(
        table_name: str,
        select_fields: list | None = None,
        conditions: dict[str, Any] | None = None,
        order_by: str | list | None = None,
        limit: int | None = None,
    ) -> (str, dict[str, Any]):  # type: ignore
        """Dynamically construct and return an SQL SELECT query."""
        select_clause = ", ".join(select_fields) if select_fields else "*"
        query = f"SELECT {select_clause} FROM {table_name}"

        values = {}
        if conditions:
            where_clauses = []
            for key, value in conditions.items():
                where_clauses.append(f"{key} = :{key}")
                values[key] = value
            query += " WHERE " + " AND ".join(where_clauses)

        if order_by:
            if isinstance(order_by, list):
                order_by_clause = ", ".join(order_by)
            else:
                order_by_clause = order_by
            query += f" ORDER BY {order_by_clause}"

        if limit:
            query += f" LIMIT {limit}"

        return query, values

    @staticmethod
    def generate_create_query(
        table_name: str, fields: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Dynamically construct and return an SQL INSERT query."""
        if not fields:
            raise ValueError("Fields dictionary cannot be empty")

        columns = ", ".join(fields.keys())
        placeholders = ", ".join(f":{key}" for key in fields)

        create_query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        RETURNING *
        """

        return create_query, fields

    @staticmethod
    async def save_uploaded_file(
        file: UploadFile,
        allowed_types: list[str] | None = None,
        max_size_mb: int = 5,
    ) -> tuple[bytes, int, str]:
        """Save an uploaded file to disk and return file content, size, and path."""
        if allowed_types and file.content_type not in allowed_types:
            raise CustomizedValueError(
                f"Invalid file format. Only {', '.join(allowed_types)} are supported."
            )

        content = await file.read()
        file_size = len(content)

        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise CustomizedValueError(f"File size exceeds the {max_size_mb}MB limit.")

        upload_path = Path(UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)

        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = upload_path / unique_filename

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return content, file_size, str(file_path)
