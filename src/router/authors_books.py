from fastapi import APIRouter, Body, Depends, HTTPException

from src.exceptions import ObjectAlreadyExists
from src.schemas.authors import AuthorAddRequest
from src.services.authors_books import AuthorsBooksService, get_authors_books_service


router = APIRouter(prefix="/authors", tags=["Авторы и книги"])


@router.post("", summary="Добавить автора и его книги", status_code=201)
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
    try:
        await service.create_author_with_books(data)
    except ObjectAlreadyExists:
        raise HTTPException(status_code=409, detail="Автор с таким именем уже существует")
    
    return {"status": "ok"}
