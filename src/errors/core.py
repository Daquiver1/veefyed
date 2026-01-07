"""Custom error classes for handling database errors."""

from starlette import status


class CoreError(Exception):
    """Base class for database errors."""

    def __init__(self, message: str, status_code: int) -> None:
        """Initializes the error with a message and status code."""
        self.message = message
        self.status_code = status_code


class InternalServerError(CoreError):
    """Raised when an internal server error occurs."""

    def __init__(self, additional_message: str | None = None) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = "Internal Server Error"
        if additional_message:
            message += f": {additional_message}"
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvalidTokenError(CoreError):
    """Raised when an entity is not found in the database."""

    def __init__(self, message: str | None = None) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        if not message:
            message = "Invalid Token: Could not validate credentials"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class CustomizedValueError(CoreError):
    """Raised when an entity is not found in the database."""

    def __init__(self, additional_message: str | None = None) -> None:
        """Initializes the error with the entity name and a dynamic message."""
        message = "Value Error"
        if additional_message:
            message += f": {additional_message}"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
