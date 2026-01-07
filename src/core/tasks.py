"""Core task: Connect and Disconnect to db when application starts and stops."""

from collections.abc import Callable

from fastapi import FastAPI

from src.core.logger_config import app_logger
from src.db.repositories.tasks import (
    close_redis_connection,
    connect_database,
    connect_to_redis,
    disconnect_database,
)


def create_start_app_handler(app: FastAPI) -> Callable:
    """Connect to db."""

    async def start_app() -> None:
        await connect_database(app)
        await connect_to_redis(app)

        app_logger.info("Application started")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    """Disconnect db."""

    async def stop_app() -> None:
        await disconnect_database(app)
        await close_redis_connection(app)

        app_logger.info("Application stopped")

    return stop_app
