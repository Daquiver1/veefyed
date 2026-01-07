"""Unit tests for helper functions."""

from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from src.errors.core import CustomizedValueError
from src.utils.helpers import Helpers


class TestHelpers:
    """Test Helpers class."""

    @pytest.mark.asyncio
    async def test_generate_uuid(self):
        """Test UUID generation."""
        uuid1 = await Helpers.generate_uuid()
        uuid2 = await Helpers.generate_uuid()
        
        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert uuid1 != uuid2
        assert len(uuid1) == 36 

    def test_hash_api_key(self):
        """Test API key hashing."""
        api_key = "test-api-key-12345"
        hashed = Helpers.hash_api_key(api_key)
        
        assert isinstance(hashed, str)
        assert hashed != api_key
        assert hashed.startswith("$argon2id$")

    def test_hash_api_key_different_inputs(self):
        """Test that different API keys produce different hashes."""
        hash1 = Helpers.hash_api_key("key1")
        hash2 = Helpers.hash_api_key("key2")
        assert hash1 != hash2

    def test_generate_select_query_simple(self):
        """Test simple SELECT query generation."""
        query, values = Helpers.generate_select_query(
            table_name="images",
        )
        assert "SELECT * FROM images" in query
        assert values == {}

    def test_generate_select_query_with_conditions(self):
        """Test SELECT query with WHERE conditions."""
        query, values = Helpers.generate_select_query(
            table_name="images",
            conditions={"id": "123", "is_deleted": False},
        )
        assert "SELECT * FROM images" in query
        assert "WHERE" in query
        assert "id = :id" in query
        assert "is_deleted = :is_deleted" in query
        assert values == {"id": "123", "is_deleted": False}

    def test_generate_select_query_with_fields(self):
        """Test SELECT query with specific fields."""
        query, values = Helpers.generate_select_query(
            table_name="images",
            select_fields=["id", "content_type", "file_size"],
        )
        assert "SELECT id, content_type, file_size FROM images" in query

    def test_generate_select_query_with_order_by(self):
        """Test SELECT query with ORDER BY."""
        query, values = Helpers.generate_select_query(
            table_name="images",
            order_by="created_at DESC",
        )
        assert "ORDER BY created_at DESC" in query

    def test_generate_select_query_with_limit(self):
        """Test SELECT query with LIMIT."""
        query, values = Helpers.generate_select_query(
            table_name="images",
            limit=10,
        )
        assert "LIMIT 10" in query

    def test_generate_create_query(self):
        """Test INSERT query generation."""
        fields = {
            "id": "123",
            "content_type": "image/jpeg",
            "file_size": 1024,
        }
        query, values = Helpers.generate_create_query(
            table_name="images",
            fields=fields,
        )
        assert "INSERT INTO images" in query
        assert "id, content_type, file_size" in query
        assert ":id, :content_type, :file_size" in query
        assert "RETURNING *" in query
        assert values == fields

    def test_generate_create_query_empty_fields(self):
        """Test INSERT query with empty fields raises error."""
        with pytest.raises(ValueError, match="Fields dictionary cannot be empty"):
            Helpers.generate_create_query(table_name="images", fields={})

    @pytest.mark.asyncio
    async def test_save_uploaded_file_valid(self):
        """Test saving valid uploaded file."""
        content = b"fake image content"
        file = UploadFile(
            filename="test.jpg",
            file=BytesIO(content),
            headers={"content-type": "image/jpeg"},
        )
        
        file_size, storage_path = await Helpers.save_uploaded_file(
            file=file,
            allowed_types=["image/jpeg", "image/png"],
            max_size_mb=5,
        )
        
        assert file_size == len(content)
        assert storage_path.endswith(".jpg")
        assert Path(storage_path).exists()
        
        Path(storage_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_save_uploaded_file_no_filename(self):
        """Test saving file without filename."""
        file = UploadFile(filename=None, file=BytesIO(b"content"))
        
        with pytest.raises(CustomizedValueError, match="No file was uploaded"):
            await Helpers.save_uploaded_file(file=file)

    @pytest.mark.asyncio
    async def test_save_uploaded_file_invalid_type(self):
        """Test saving file with invalid content type."""
        file = UploadFile(
            filename="test.pdf",
            file=BytesIO(b"content"),
            headers={"content-type": "application/pdf"},
        )
        
        with pytest.raises(CustomizedValueError, match="Invalid file format"):
            await Helpers.save_uploaded_file(
                file=file,
                allowed_types=["image/jpeg", "image/png"],
            )

    @pytest.mark.asyncio
    async def test_save_uploaded_file_empty(self):
        """Test saving empty file."""
        file = UploadFile(
            filename="test.jpg",
            file=BytesIO(b""),
            headers={"content-type": "image/jpeg"},
        )
        
        with pytest.raises(CustomizedValueError, match="Uploaded file is empty"):
            await Helpers.save_uploaded_file(file=file)

    @pytest.mark.asyncio
    async def test_save_uploaded_file_exceeds_size(self):
        """Test saving file that exceeds size limit."""
        large_content = b"x" * (6 * 1024 * 1024)
        file = UploadFile(
            filename="large.jpg",
            file=BytesIO(large_content),
            headers={"content-type": "image/jpeg"},
        )
        
        with pytest.raises(CustomizedValueError, match="File size exceeds"):
            await Helpers.save_uploaded_file(
                file=file,
                allowed_types=["image/jpeg"],
                max_size_mb=5,
            )
