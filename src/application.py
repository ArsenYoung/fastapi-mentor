from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.exceptions import AppError, ConflictError, NotFoundError
from src.router.healthcheck import router as healthcheck_router
from src.router.authors_books import router as authors_books_router
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
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=JSONResponse,
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        request: Request,
        exc: NotFoundError
    ):
        return get_error_response(
            status_code=404,
            code=getattr(exc, "code", "not_found_error"),
            message=getattr(exc, "message", "Объект не найден"),
            details=getattr(exc, "details", None)
        )
    
    @app.exception_handler(ConflictError)
    async def conflict_handler(
        request: Request,
        exc: ConflictError
    ):
        return get_error_response(
            status_code=409,
            code=getattr(exc, "code", "conflict_error"),
            message=getattr(exc, "message", "Конфликт"),
            details=getattr(exc, "details", None)
        )
    
    @app.exception_handler(AppError)
    async def unexpected_error_handler(
        request: Request,
        exc: AppError
    ):
        return get_error_response(
            status_code=500,
            code="unexpected_error",
            message="Внутренняя ошибка сервера",
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

    return app
