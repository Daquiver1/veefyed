"""Middleware configuration for the application."""

import logging
import time
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from src.core.config import ENV

app_logger = logging.getLogger("app")
security_logger = logging.getLogger("security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add essential security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        if ENV == "PROD":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "connect-src 'self';"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting."""

    def __init__(self, app, calls: int = 100, period: int = 60) -> None:
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Use sliding window
        if ENV == "PROD":
            client_ip = self.get_client_ip(request)
            current_time = time.time()

            self.clients = {
                ip: calls
                for ip, calls in self.clients.items()
                if current_time - calls[-1] < self.period
            }

            if client_ip in self.clients:
                calls = self.clients[client_ip]
                recent_calls = [
                    call for call in calls if current_time - call < self.period
                ]

                if len(recent_calls) >= self.calls:
                    security_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    return JSONResponse(
                        status_code=429, content={"detail": "Rate limit exceeded"}
                    )

                recent_calls.append(current_time)
                self.clients[client_ip] = recent_calls
            else:
                self.clients[client_ip] = [current_time]

        return await call_next(request)

    def get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering proxies."""
        # Heeroku only, if not using a proxy, this will return the direct client IP
        # Otherwise, it will return the first IP in the X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host # type: ignore


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced request logging with performance metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_ip = self.get_client_ip(request)
        method = request.method
        path = request.url.path

        app_logger.info(f"Request: {method} {path} | IP: {client_ip}")

        response = await call_next(request)

        process_time = time.time() - start_time
        status_code = response.status_code

        app_logger.info(
            f"Response: {status_code} | Time: {process_time:.3f}s | Path: {path}"
        )

        response.headers["X-Process-Time"] = str(process_time)

        if process_time > 1.0:
            app_logger.warning(
                f"Slow request: {method} {path} took {process_time:.3f}s"
            )

        return response

    def get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering proxies."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host # type: ignore


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware."""
    # if ENV == "PROD":
    #     app.add_middleware(
    #         TrustedHostMiddleware,
    #         allowed_hosts=[],
    #     )

    # app.add_middleware(SecurityHeadersMiddleware)

    # app.add_middleware(RateLimitMiddleware, calls=100, period=60)

    # app.add_middleware(GZipMiddleware, minimum_size=1000)
    origins = ["http://localhost:3000", "http://localhost:3001"] if ENV == "DEV" else []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
        ],
        expose_headers=["X-Process-Time"],
    )

    # app.add_middleware(RequestLoggingMiddleware)