"""Database Connect Tasks"""

import logging

from databases import Database
from fastapi import FastAPI

from src.core.config import DATABASE_URL, REDIS_URL
from src.services.third_party.redis_client import RedisClient

app_logger = logging.getLogger("app")


async def connect_database(app: FastAPI) -> None:
    """Connect to DB"""
    try:
        database = Database(DATABASE_URL)
        await database.connect()
        app.state._db = database
        app_logger.info("Connected to sqlite db.")
    except Exception as e:
        app_logger.exception("Failed to connect to sqlite db", exc_info=e)


async def disconnect_database(app: FastAPI) -> None:
    """Close db."""
    try:
        await app.state._db.disconnect()
        app_logger.info("Disconnected from postgresql db")
    except Exception as e:
        app_logger.exception("Error disconnecting from sqlite", exc_info=e)


async def connect_to_redis(app: FastAPI) -> None:
    """Connect to redis."""
    try:
        app_logger.info("Connecting to redis database")
        app.state._redis_client = RedisClient(REDIS_URL)
        app_logger.info("Connected to redis database")
    except Exception as e:
        app_logger.info("--- Redis Authenication Error")
        app_logger.exception(e)
        app.state._redis_client = None
        app_logger.info("--- Redis Authenication Error")


async def close_redis_connection(app: FastAPI) -> None:
    """Connect to redis."""
    try:
        app_logger.info("Disconnecting from redis database")
        app.state._redis_client.redis.close()
        app_logger.info("Disconnected from redis database")
    except Exception as e:
        app_logger.info("--- Redis AuthenTication Error")
        app_logger.exception(e)
