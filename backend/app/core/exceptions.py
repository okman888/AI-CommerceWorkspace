"""Custom exceptions and exception handlers."""
from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception."""
    def __init__(self, message: str = "Resource not found", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class UnauthorizedException(AppException):
    """Unauthorized exception."""
    def __init__(self, message: str = "Unauthorized", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class ForbiddenException(AppException):
    """Forbidden exception."""
    def __init__(self, message: str = "Forbidden", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class BadRequestException(AppException):
    """Bad request exception."""
    def __init__(self, message: str = "Bad request", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class ValidationException(AppException):
    """Validation exception."""
    def __init__(self, message: str = "Validation error", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "details": {"message": str(exc)} if app.debug else None,
            }
        )
