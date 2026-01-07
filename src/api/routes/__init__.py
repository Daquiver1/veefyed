"""Route configuration for the application."""

from fastapi import FastAPI

from src.api.routes.review import review_router
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
            "service": "QuiverFood API",
        }

    app.include_router(
        review_router,
        prefix=f"{api_prefix}/review",
        tags=["Reviews"],
    )
