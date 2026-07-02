from contextlib import AsyncExitStack
import time

import structlog

from src.config import Settings
from src.logging import configure_logging
from src.logging_context import (
    get_new_request_id,
    bind_request_context,
    clear_request_context,
)

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from src.exceptions.base import (
    AlreadyExistsException,
    AppException,
    ObjectNotFoundException,
)
from src.router.healthcheck import router as healthcheck_router
from src.router.authors_books import router as authors_books_router
from src.router.persons_passports import router as persons_passports_router
from src.router.students_courses import router as students_courses_router
from src.schemas.errors import ErrorDetailsType, ErrorPayload, ErrorResponse


def get_error_response(
    status_code: int,
    message: str,
    details: ErrorDetailsType = None,
) -> JSONResponse:
    error_response = ErrorResponse(
        error=ErrorPayload(
            message=message,
            details=details,
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(exclude_none=True),
    )


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    settings = Settings()
    configure_logging(settings)
    logger = structlog.get_logger()

    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=JSONResponse,
    )

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        async with AsyncExitStack() as stack:
            request_id = get_new_request_id()
            bind_request_context(request_id)
            stack.callback(clear_request_context)

            start = time.perf_counter()

            logger.info(
                "request_started",
                method=request.method,
                path=request.url.path,
            )

            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            response.headers["X-Request-ID"] = request_id

            logger.info(
                "request_finished",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            return response

    @app.exception_handler(ObjectNotFoundException)
    async def not_found_handler(
        request: Request,
        exc: ObjectNotFoundException
    ):
        logger.warning(
            "object_not_found",
            path=request.url.path,
            message=getattr(exc, "message", "Object not found")
        )
        return get_error_response(
            status_code=404,
            message=getattr(exc, "message", "Object not found"),
            details=getattr(exc, "details", None),
        )
    
    @app.exception_handler(AlreadyExistsException)
    async def already_exists_handler(
        request: Request,
        exc: AlreadyExistsException
    ):
        logger.warning(
            "already_exists",
            path=request.url.path,
            message=getattr(exc, "message", "Object already exists")
        )
        return get_error_response(
            status_code=409,
            message=getattr(exc, "message", "Object already exists"),
            details=getattr(exc, "details", None),
        )
    
    @app.exception_handler(AppException)
    async def unexpected_error_handler(
        request: Request,
        exc: AppException
    ):
        logger.exception(
            "app_exception",
            path=request.url.path,
            message=getattr(exc, "message", "Unexpected error"),
        )
        return get_error_response(
            status_code=500,
            message="Unexpected error",
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(healthcheck_router)
    app.include_router(authors_books_router)
    app.include_router(persons_passports_router)
    app.include_router(students_courses_router)

    return app
