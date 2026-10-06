import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)

from app.core.exceptions import AppError


logger = logging.getLogger(__name__)


def _error_response(
    status_code: int,
    detail: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    # Same {"detail": ...} shape FastAPI uses for HTTPException.
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
        headers=headers,
    )


async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        headers=exc.headers,
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
) -> JSONResponse:
    # Constraint violations not already translated by a repository,
    # e.g. a concurrent request deleting a referenced row.
    logger.warning(
        "Integrity error on %s %s: %s",
        request.method,
        request.url.path,
        exc.orig,
    )

    return _error_response(
        status_code=status.HTTP_409_CONFLICT,
        detail="Request conflicts with the current state of the resource",
    )


async def database_error_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception(
        "Database error on %s %s",
        request.method,
        request.url.path,
    )

    # Lost/refused connections, lock timeouts and deadlocks are transient;
    # anything else is a bug.
    if isinstance(exc, OperationalError) or (
        isinstance(exc, DBAPIError) and exc.connection_invalidated
    ):
        return _error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable",
        )

    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
    )


async def unhandled_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )

    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
