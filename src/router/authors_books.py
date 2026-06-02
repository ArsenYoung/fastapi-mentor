from fastapi import APIRouter, Depends, status

from src.dependencies import get_authors_books_service
from src.schemas.authors import AuthorAddRequest, AuthorPatch, AuthorRead
from src.schemas.common import CommonResponse
from src.services.authors_books import AuthorsBooksService


router = APIRouter(prefix="/authors", tags=["Авторы и книги 1-М"])


@router.post("", summary="Добавить автора и его книги", status_code=status.HTTP_201_CREATED)
async def post_author_with_books(
    data: AuthorAddRequest,
    service: AuthorsBooksService = Depends(get_authors_books_service)
) -> CommonResponse:
    await service.create_author_with_books(data)
    return CommonResponse

@router.get("/{author_id}", response_model=AuthorRead, summary="Получить автора и его книги", status_code=status.HTTP_200_OK)
async def get_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
) -> AuthorRead:
    return await service.get_author_with_books(author_id)

@router.delete("/{author_id}", summary="Удалить автора и его книги", status_code=status.HTTP_204_NO_CONTENT)
async def del_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
) -> None:
    await service.del_author_with_books(author_id)

@router.patch("/{author_id}", summary="Изменить данные автора", status_code=status.HTTP_200_OK)
async def update_author_with_books(
    author_id: int,
    data: AuthorPatch,
    service: AuthorsBooksService = Depends(get_authors_books_service),
) -> CommonResponse:
    await service.update_author_with_books(author_id, data)
    return CommonResponse
