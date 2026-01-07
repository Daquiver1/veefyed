"""Decorator for database operations (SQLite-compatible)."""

import logging
import sqlite3
from functools import wraps
from typing import Any

from sqlalchemy.exc import DataError, IntegrityError, OperationalError

from src.errors.core import InternalServerError, InvalidTokenError
from src.errors.database import (
    AlreadyExistsError,
    BadRequestError,
    DataTypeError,
    ForeignKeyError,
    GeneralDatabaseError,
    IncorrectCredentialsError,
    NotFoundError,
)

app_logger = logging.getLogger("app")


def handle_get_database_exceptions(entity_name: str) -> callable:  # type: ignore
    """Decorator to handle database exceptions for get operations (SQLite)."""

    def decorator(func: callable) -> callable:  # type: ignore
        @wraps(func)
        async def wrapper(self, *args: tuple, **kwargs: dict[str, Any]) -> Any:
            logger = app_logger
            try:
                return await func(self, *args, **kwargs)
            except sqlite3.IntegrityError as e:
                logger.exception(f"IntegrityError for {entity_name}")
                raise DataTypeError(entity_name=entity_name) from e
            except DataError as e:
                logger.exception(f"DataError for {entity_name}")
                raise DataTypeError(entity_name=entity_name) from e
            except OperationalError as e:
                logger.exception(f"OperationalError for {entity_name}")
                raise GeneralDatabaseError(entity_name=entity_name) from e
            except ValueError as e:
                logger.exception(f"ValueError for {entity_name}")
                raise BadRequestError(
                    f"Bad Request: Invalid details for {entity_name}"
                ) from e
            except NotFoundError:
                logger.exception(f"NotFoundError for {entity_name}")
                raise
            except IncorrectCredentialsError:
                logger.exception(f"Incorrect credentials for {entity_name}")
                raise
            except InvalidTokenError:
                logger.exception(f"Invalid token for {entity_name}")
                raise
            except Exception as e:
                logger.exception(f"Unexpected error for {entity_name}")
                raise InternalServerError(
                    additional_message="Unexpected error. Try again."
                ) from e

        return wrapper

    return decorator


def handle_post_database_exceptions(
    entity_name: str,
    foreign_key_entity: str = "Entity",
    already_exists_entity: str = "Entity",
) -> callable:  # type: ignore
    """Decorator to handle database exceptions for post operations (SQLite)."""

    def decorator(func: callable) -> callable:  # type: ignore
        @wraps(func)
        async def wrapper(self, *args: tuple, **kwargs: dict[str, Any]) -> Any:
            logger = app_logger
            try:
                return await func(self, *args, **kwargs)
            except IntegrityError as e:
                logger.exception(f"IntegrityError for {entity_name}")
                msg = str(e.orig).lower() if e.orig else ""
                if "unique" in msg:
                    raise AlreadyExistsError(entity_name=already_exists_entity) from e
                if "foreign key" in msg:
                    raise ForeignKeyError(entity_name=foreign_key_entity) from e
                raise GeneralDatabaseError(entity_name=entity_name) from e
            except DataError as e:
                logger.exception(f"DataError for {entity_name}")
                raise DataTypeError(entity_name=entity_name) from e
            except OperationalError as e:
                logger.exception(f"OperationalError for {entity_name}")
                raise GeneralDatabaseError(entity_name=entity_name) from e
            except ValueError as e:
                logger.exception(f"ValueError for {entity_name}")
                raise BadRequestError(
                    f"Bad Request: Invalid details for {entity_name}"
                ) from e
            except NotFoundError:
                logger.exception(f"NotFoundError for {entity_name}")
                raise
            except IncorrectCredentialsError:
                logger.exception(f"Incorrect credentials for {entity_name}")
                raise
            except InvalidTokenError:
                logger.exception(f"Invalid token for {entity_name}")
                raise
            except Exception as e:
                logger.exception(f"Unexpected error for {entity_name}")
                raise InternalServerError(
                    additional_message="Unexpected error. Try again."
                ) from e

        return wrapper

    return decorator
