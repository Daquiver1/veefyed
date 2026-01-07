"""Auth  module."""

import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse

from fastapi import Request
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    ENV,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from src.errors.core import InvalidTokenError

app_logger = logging.getLogger("app")


class AuthService:
    """Auth service."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """Create access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, data: dict) -> str:
        """Create refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    async def get_access_token(self, sub: str) -> str:
        """Gets Access Token"""
        return self.create_access_token({"sub": sub})

    async def get_token_data(self, token: str) -> dict:
        """Gets token data"""
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    async def verify_token(
        self,
        token: str,
        request: Request,
        credentials_exception: Exception = InvalidTokenError(),
    ) -> str:
        """Verifies tokens."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

            if ENV == "PROD":
                current_origin = request.headers.get("origin", "")
                token_origin = payload.get("origin", "")
                referer = request.headers.get("referer", "")

                if not current_origin and referer:
                    parsed_referer = urlparse(referer)
                    current_origin = (
                        f"{parsed_referer.scheme}://{parsed_referer.netloc}"
                    )

                is_sensitive = request.url.path.startswith(
                    "/admin"
                ) or request.method in ["POST", "PUT", "DELETE"]

                if (
                    is_sensitive
                    and token_origin
                    and current_origin
                    and current_origin != token_origin
                ):
                    app_logger.warning(
                        f"Origin mismatch: Token origin {token_origin}, Request origin/referer {current_origin}"
                    )
                    raise InvalidTokenError("Invalid request context")

                # Check IP for highly sensitive operations
                if request.url.path.startswith("/admin"):
                    current_ip = request.client.host if request.client else ""
                    token_ip = payload.get("client_ip")

                    if token_ip and current_ip != token_ip:
                        app_logger.warning(
                            f"IP mismatch for admin request: Token IP {token_ip}, Request IP {current_ip}"
                        )
                        raise InvalidTokenError("Invalid request context")
            user_id = payload.get("user_id")
            if not user_id:
                raise credentials_exception  # noqa
        except JWTError:
            raise credentials_exception

        return user_id

    async def verify_refresh_token(
        self,
        refresh_token: str,
        credentials_exception: Exception = InvalidTokenError(),
    ) -> str:
        """Verifies refresh token and returns user_id."""
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            token_type = payload.get("type")

            if not user_id or token_type != "refresh":
                app_logger.warning(
                    "Invalid refresh token: missing user_id or incorrect type"
                )
                raise credentials_exception

        except JWTError as e:
            app_logger.warning(f"JWT error while verifying refresh token: {str(e)}")
            raise credentials_exception

        return user_id

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Method to verify passwords"""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def get_password_hash(self, password: str) -> str:
        """Method to hash passwords"""
        return self.pwd_context.hash(password)
