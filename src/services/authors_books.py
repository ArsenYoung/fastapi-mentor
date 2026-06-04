from sqlalchemy.exc import IntegrityError
from src.exceptions.books import BookNotFoundError
from src.schemas.authors import Author, AuthorAddRequest, AuthorPatch, AuthorsPage
from src.schemas.errors import AuthorConflictError, AuthorNotFoundError


class AuthorsBooksService():
    def __init__(self, repo):
        self.repo = repo
    
    async def create_author_with_books(self, data: AuthorAddRequest) -> None:
        try:
            await self.repo.create_author_with_books(data)
        except IntegrityError as exc:
            raise AuthorConflictError from exc

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self.repo.get_author_with_books(author_id)
        if author is None:
            raise AuthorNotFoundError()
        return author
    
    async def get_all_authors_with_books(self, limit: int, offset: int) -> tuple[list[Author], int]:
        items, total = await self.repo.get_all_authors_with_books(limit, offset)
        return AuthorsPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )
    
    async def del_author_with_books(self, author_id: int) -> None:
        is_deleted = await self.repo.del_author_with_books(author_id)
        if not is_deleted:
            raise AuthorNotFoundError() 

    async def update_author_with_books(self, author_id, data: AuthorPatch) -> None:
        try:
            result = await self.repo.update_author_with_books(author_id, data)
        except IntegrityError as exc:
            raise AuthorConflictError()

        if not result.author_found:
            raise AuthorNotFoundError()
        
        if not result.books_found:
            raise BookNotFoundError()