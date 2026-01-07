"""Route configuration for the application."""

from fastapi import FastAPI

from src.api.routes.api_key import api_key_router
from src.api.routes.image import image_router
from src.api.routes.image_analysis import analysis_router
from src.core import config


def setup_routes(app: FastAPI) -> None:
    """Configure all application routes."""
    api_prefix = config.API_PREFIX

    @app.get("/", name="index")
    async def index() -> dict:
        return {
            "message": "Veefyed API is running!",
            "status": "success",
            "docs": "Visit /docs to view API documentation",
        }

    @app.get("/health")
    async def health_check() -> dict:
        return {
            "status": "healthy",
            "database": "connected",
            "service": "Veefyed API",
        }

    app.include_router(api_key_router, prefix=f"{api_prefix}/api-keys", tags=["API Keys"])
    app.include_router(image_router, prefix=f"{api_prefix}/images", tags=["Images"])
    app.include_router(
        analysis_router, prefix=f"{api_prefix}/image-analysis", tags=["Image Analysis"]
    )
