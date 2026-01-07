"""Decorator for get db operations to handle database exceptions."""

import logging
from functools import wraps
from typing import Any

from asyncpg import (
    DataError,
    ForeignKeyViolationError,
    PostgresError,
    UniqueViolationError,
)

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
    """Decorator to handle database exceptions for get operations."""

    def decorator(func: callable) -> callable:  # type: ignore
        @wraps(func)
        async def wrapper(
            self,
            *args: tuple,
            **kwargs: dict[str, Any],  # noqa
        ) -> callable:  # type: ignore
            logger = app_logger
            try:
                return await func(self, *args, **kwargs)
            except DataError as e:
                logger.exception(f"DataError for {entity_name}")
                raise DataTypeError(entity_name=entity_name) from e
            except PostgresError as e:
                logger.exception(f"PostgresError for {entity_name}")
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
                logger.exception(f"Invalid jwt token for {entity_name}")
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
    """Decorator to handle database exceptions for post operations."""

    def decorator(func: callable) -> callable:  # type: ignore
        @wraps(func)
        async def wrapper(
            self,
            *args: tuple,
            **kwargs: dict[str, Any],  # noqa
        ) -> callable:  # type: ignore
            logger = app_logger
            try:
                return await func(self, *args, **kwargs)
            except UniqueViolationError as e:
                logger.exception(f"UniqueViolationError for {entity_name}")
                if "email" in str(e):
                    raise AlreadyExistsError(entity_name="Email") from e
                if "referral_code" in str(e):
                    raise AlreadyExistsError(entity_name="Referral Code") from e
                raise AlreadyExistsError(entity_name=already_exists_entity) from e
            except ForeignKeyViolationError as e:
                logger.exception(f"ForeignKeyViolationError for {entity_name}")
                raise ForeignKeyError(entity_name=foreign_key_entity) from e
            except DataError as e:
                logger.exception(f"DataError for {entity_name}")
                raise DataTypeError(entity_name=entity_name) from e
            except PostgresError as e:
                logger.exception(f"PostgresError for {entity_name}")
                raise GeneralDatabaseError(entity_name=entity_name) from e
            except NotFoundError:
                logger.exception(f"NotFoundError for {entity_name}")
                raise
            except ValueError as e:
                logger.exception(f"ValueError for {entity_name}")
                raise BadRequestError(
                    f"Bad Request: Invalid details for {entity_name}"
                ) from e
            except IncorrectCredentialsError:
                logger.exception(f"Incorrect credentials for {entity_name}")
                raise
            except InvalidTokenError:
                logger.exception(f"Invalid jwt token for {entity_name}")
                raise
            except Exception as e:
                logger.exception(f"Unexpected error for {entity_name}")
                raise InternalServerError(
                    additional_message="Unexpected error. Try again."
                ) from e

        return wrapper

    return decorator
