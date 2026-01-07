"""Main module for FastAPI application."""

import logging

from fastapi import FastAPI

from src.api.exception_handlers import setup_exception_handlers
from src.api.middleware import setup_middleware
from src.api.routes import setup_routes
from src.core import config, tasks

app = FastAPI()
request_logger = logging.getLogger("request")


def setup_event_handlers(app: FastAPI) -> None:
    """Configure all event handlers."""
    app.add_event_handler("startup", tasks.create_start_app_handler(app))
    app.add_event_handler("shutdown", tasks.create_stop_app_handler(app))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)

    docs_url = None if config.ENV == "PROD" else "/docs"
    redoc_url = None if config.ENV == "PROD" else "/redoc"

    setup_routes(app)
    setup_middleware(app)
    setup_exception_handlers(app)
    setup_event_handlers(app)

    app.docs_url = docs_url
    app.redoc_url = redoc_url
    return app


app = create_app()
