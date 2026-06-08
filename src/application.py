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
from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.app_exception import AppException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
from src.router.healthcheck import router as healthcheck_router
from src.router.authors_books import router as authors_books_router
from src.router.persons_passports import router as persons_passports_router
from src.router.students_courses import router as students_courses_router
from src.schemas.errors import ErrorPayload, ErrorResponse


def get_error_response(
    status_code: int,
    code: str,
    message: str,
    details: str = None
) -> JSONResponse:
    error_response = ErrorResponse(
        error=ErrorPayload(
            code=code,
            message=message,
            details=details
    ))
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
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
        request_id = get_new_request_id()
        bind_request_context(request_id)

        start = time.perf_counter()

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms
            )
            raise
        else:
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
        finally:
            clear_request_context()

    @app.exception_handler(ObjectNotFoundException)
    async def not_found_handler(
        request: Request,
        exc: ObjectNotFoundException
    ):
        logger.warning(
            "object_not_found",
            path=request.url.path,
            error_code=getattr(exc, "code", "object_not_found_exception"),
            message=getattr(exc, "message", "Object not found")
        )
        return get_error_response(
            status_code=404,
            code=getattr(exc, "code", "object_not_found_exception"),
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
            error_code=getattr(exc, "code", "already_exists_exception"),
            message=getattr(exc, "message", "Object already exists")
        )
        return get_error_response(
            status_code=409,
            code=getattr(exc, "code", "already_exists_exception"),
            message=getattr(exc, "message", "A student with this record book number already exists"),
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
            error_code=getattr(exc, "code", "unexpected_error"),
            message=getattr(exc, "message", "Unexpected error"),
        )
        return get_error_response(
            status_code=500,
            code="unexpected_error",
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
