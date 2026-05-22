from fastapi import APIRouter, Body, Depends, HTTPException

from src.exceptions import ObjectAlreadyExists, ObjectNotFound
from src.schemas.authors import AuthorAddRequest, AuthorRead
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

@router.get("/{author_id}", response_model=AuthorRead, summary="Получить автора и его книги", status_code=200)
async def get_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
):
    try:
        await service.get_author_with_books(author_id)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return await service.get_author_with_books(author_id)

@router.delete("/{author_id}", summary="Удалить автора и его книги", status_code=200)
async def del_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
):
    try:
        await service.del_author_with_books(author_id)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return {"status": "ok"}