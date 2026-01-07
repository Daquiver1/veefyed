"""Custom error classes for handling database errors."""

from starlette import status

from src.errors.core import CoreError


class DatabaseError(CoreError):
    """Base class for database errors."""

    def __init__(self, message: str, status_code: int) -> None:
        """Initializes the error with a message and status code."""
        super().__init__(message, status_code)


class GeneralDatabaseError(DatabaseError):
    """General error class for database errors."""

    def __init__(self, entity_name: str) -> None:
        """Initializes the error with a generic message and status code."""
        message = f"An error occurred with db entity {entity_name.capitalize()}"
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AlreadyExistsError(DatabaseError):
    """Raised when trying to create a duplicate entity."""

    def __init__(self, entity_name: str) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = f"{entity_name.capitalize()} already exists"
        super().__init__(message, status.HTTP_409_CONFLICT)


class NotFoundError(DatabaseError):
    """Raised when an entity is not found in the database."""

    def __init__(self, entity_name: str, entity_identifier: str) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = f"{entity_name.capitalize()} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class BadRequestError(DatabaseError):
    """Raised when an entity is not found in the database."""

    def __init__(self, additional_message: str) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = f"Bad request: {additional_message}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class IncorrectCredentialsError(DatabaseError):
    """Raised when an entity is not found in the database."""

    def __init__(self) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = "Incorrect credentials"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ForeignKeyError(DatabaseError):
    """Raised when trying to delete an entity with foreign key constraints."""

    def __init__(self, entity_name: str) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = f"{entity_name.capitalize()} does not exist."
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class FailedToCreateEntityError(DatabaseError):
    """Raised when trying to delete an entity with foreign key constraints."""

    def __init__(self, entity_name: str) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = f"Failed to create {entity_name.capitalize()}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class FailedToCreateUpdateQueryError(DatabaseError):
    """Raised when trying to delete an entity with foreign key constraints."""

    def __init__(self, entity_name: str) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = f"Failed to create update query for {entity_name.capitalize()}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class InvalidSearchCriteriaError(DatabaseError):
    """Raised when no valid search criteria are provided for a database query."""

    def __init__(self, entity_name: str | None = None) -> None:
        """Initializes the error with an optional entity name and a dynamic message."""
        message = "No valid search criteria provided"
        if entity_name:
            message += f" for {entity_name.capitalize()}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class DataTypeError(DatabaseError):
    """Raised when no valid search criteria are provided for a database query."""

    def __init__(self, entity_name: str | None = None) -> None:
        """Initializes the error with an optional entity name and a dynamic message."""
        message = "Invalid data type"
        if entity_name:
            message += f" for {entity_name.capitalize()}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
