from fastapi import APIRouter, Depends, Query, status

from src.dependencies import get_authors_books_service
from src.schemas.authors import Author, AuthorCreate, AuthorsPaginatedList, AuthorUpdate
from src.schemas.common import CommonResponse
from src.services.authors_books import AuthorsBooksService


router = APIRouter(prefix="/authors", tags=["Authors and Books 1-M"])


@router.post("", summary="Create an author and their books", status_code=status.HTTP_201_CREATED)
async def create_author_with_books(
    data: AuthorCreate,
    service: AuthorsBooksService = Depends(get_authors_books_service)
) -> CommonResponse:
    await service.create_author_with_books(data)
    return CommonResponse

@router.get("/{author_id}", response_model=Author, summary="Get an author and their books", status_code=status.HTTP_200_OK)
async def get_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
) -> Author:
    return await service.get_author_with_books(author_id)

@router.get("", response_model=AuthorsPaginatedList, summary="Get all authors and their books", status_code=status.HTTP_200_OK)
async def get_authors_with_books_paginated_list(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: AuthorsBooksService = Depends(get_authors_books_service)
):
    return await service.get_authors_with_books_paginated_list(limit, offset)

@router.delete("/{author_id}", summary="Delete an author and their books", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author_with_books(
    author_id: int,
    service: AuthorsBooksService = Depends(get_authors_books_service)
) -> None:
    await service.delete_author_with_books(author_id)

@router.patch("/{author_id}", summary="Update author data", status_code=status.HTTP_200_OK)
async def update_author_with_books(
    author_id: int,
    data: AuthorUpdate,
    service: AuthorsBooksService = Depends(get_authors_books_service),
) -> CommonResponse:
    await service.update_author_with_books(author_id, data)
    return CommonResponse
