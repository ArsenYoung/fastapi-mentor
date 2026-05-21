from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.router.healthcheck import router as healthcheck_router
from src.router.authors_books import router as authors_books_router



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