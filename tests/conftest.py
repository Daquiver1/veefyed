"""Pytest configuration and fixtures."""

import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from databases import Database
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.services.third_party.redis_client import RedisClient


@pytest.fixture
def test_app():
    """Create test FastAPI application."""
    app = create_app()
    return app


@pytest.fixture
def client(test_app) -> Generator:
    """Create test client."""
    with TestClient(test_app) as c:
        yield c


@pytest.fixture
def mock_db() -> AsyncMock:
    """Create mock database."""
    db = AsyncMock(spec=Database)
    db.fetch_one = AsyncMock()
    db.fetch_all = AsyncMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def mock_redis() -> MagicMock:
    """Create mock Redis client."""
    redis = MagicMock(spec=RedisClient)
    return redis


@pytest.fixture
def sample_image_data():
    """Sample image data for testing."""
    return {
        "content_type": "image/jpeg",
        "file_size": 1024000,
        "storage_path": "/uploads/images/test-image.jpg",
    }


@pytest.fixture
def sample_image_id():
    """Sample image UUID for testing."""
    return "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing."""
    return {
        "image_id": "123e4567-e89b-12d3-a456-426614174000",
        "skin_type": "Oily",
        "issues": ["Acne", "Redness"],
        "confidence_score": 0.92,
        "model_version": "v1.0.0-mock",
    }
