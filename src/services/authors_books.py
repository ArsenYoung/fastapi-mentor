from src.exceptions import AuthorConflictError, NotFoundError
from src.mappers.authors_books import build_author_response
from src.repositories.authors import AuthorsRepository
from src.repositories.books import BooksRepository
from src.schemas.authors import Author, AuthorAddRequest, AuthorPatch
from src.schemas.books import BookAdd


class AuthorsBooksService():
    def __init__(self, session):
        self.authors_repo = AuthorsRepository(session)
        self.books_repo = BooksRepository(session)

    async def _get_author(self, **filter_by) -> Author:
        author = await self.authors_repo.get_one_or_none(**filter_by)
        if author is None:
            raise NotFoundError()
        return author
    
    async def _check_author_exist(self, **filter_by) -> None:
        author = await self.authors_repo.get_one_or_none(**filter_by)
        if author:
            raise AuthorConflictError()
    
    async def create_author_with_books(self, data: AuthorAddRequest) -> None:
        await self._check_author_exist(name=data.name)
        author_added = await self.authors_repo.add(data, exclude={"books"})
        books_data = [
            BookAdd(author_id=author_added.id, title=item.title)
            for item in data.books
        ]
        if books_data:
            await self.books_repo.add_bulk(books_data)

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self._get_author(id=author_id)
        books = await self.books_repo.get_all(author_id=author_id)
        return build_author_response(author, books)
    
    async def del_author_with_books(self, author_id: int) -> None:
        await self._get_author(id=author_id)
        await self.books_repo.delete(author_id=author_id)
        await self.authors_repo.delete(id=author_id)  

    async def update_author_with_books(self, author_id, data: AuthorPatch) -> None:
        await self._get_author(id=author_id)
        author_data = data.model_dump(
            exclude_unset=True,
            exclude={"books"},
        )
        if author_data:
            await self.authors_repo.update(author_data, id=author_id)

        if data.books is not None:
            for item in data.books:
                book_data = item.model_dump(
                    exclude_unset=True,
                    exclude={"id"},
                )
                if not book_data:
                    continue
                await self.books_repo.update(book_data, id=item.id, author_id=author_id)
