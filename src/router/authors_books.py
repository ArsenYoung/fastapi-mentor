from fastapi import APIRouter, Depends

from src.dependencies import get_authors_books_service
from src.schemas.authors import AuthorAddRequest, AuthorPatch, AuthorRead
from src.services.authors_books import AuthorsBooksService


router = APIRouter(prefix="/authors", tags=["Авторы и книги 1-М"])


@router.post("", summary="Добавить автора и его книги", status_code=201)
async def post_author_with_books(
    data: AuthorAddRequest,
    service: AuthorsBooksService = Depends(get_authors_books_service)
):
    await service.create_author_with_books(data)
    return {"status": "ok"}

@router.get("/{author_id}", response_model=AuthorRead, summary="Получить автора и его книги", status_code=200)
async def get_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
):
    return await service.get_author_with_books(author_id)

@router.delete("/{author_id}", summary="Удалить автора и его книги", status_code=200)
async def del_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
):
    await service.del_author_with_books(author_id)
    return {"status": "ok"}

@router.patch("/{author_id}", summary="Изменить данные автора", status_code=200)
async def update_author_with_books(
    author_id: int,
    data: AuthorPatch,
    service: AuthorsBooksService = Depends(get_authors_books_service),
):
    await service.update_author_with_books(author_id, data)
    return {"status": "ok"}
