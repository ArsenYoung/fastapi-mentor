from fastapi import APIRouter, Body, Depends

from src.db import get_session
from src.repositories.authors import AuthorsRepository
from src.repositories.books import BooksRepository
from src.schemas.authors import AuthorAddRequest
from src.schemas.books import BookAdd
from src.services.authors_books import AuthorsBooksService, get_authors_books_service


router = APIRouter(prefix="/authors", tags=["Авторы и книги"])


@router.post("", summary="Добавить автора и его книги")
async def post_author_with_books(
    data: AuthorAddRequest = Body(openapi_examples={
            "1": {
                "summary": "Лев Толстой",
                "value": {
                    "name": "Лев Толстой",
                    "books": [
                        {
                            "title": "Война и Мир"
                        },
                        {
                            "title": "Воскресенье"
                        },
                    ],
                },
            },
        }
    ),
    service: AuthorsBooksService = Depends(get_authors_books_service)
):
    return await service.create_author_with_books(data)
