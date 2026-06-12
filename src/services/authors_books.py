from collections import defaultdict

from src.schemas.authors import (
    Author,
    AuthorAddRequest,
    AuthorPatch,
    AuthorsPage,
)
from src.schemas.books import BookCreateRequest, BookPatch
from src.services.author import AuthorService
from src.services.base import BaseService
from src.services.book import BookService


class AuthorsBooksService(BaseService):
    def __init__(
        self,
        author_service: AuthorService,
        book_service: BookService,
    ):
        self.author_service = author_service
        self.book_service = book_service

    async def _sync_books(self, author_id: int, books_data: list) -> None:
        existing_books = await self.book_service.get_orm_by_author_id(author_id)
        existing_books_by_code = {book.book_code: book for book in existing_books}

        target_codes: set[str] = set()
        for item in books_data:
            target_codes.add(item.book_code)
            existing_book = existing_books_by_code.get(item.book_code)
            if existing_book is not None:
                if existing_book.title != item.title:
                    await self.book_service.update(
                        existing_book.id,
                        BookPatch(book_code=item.book_code, title=item.title),
                    )
                continue

            book_with_same_code = await self.book_service.get_any_by_code(item.book_code)
            if book_with_same_code is not None and book_with_same_code.author_id != author_id:
                self._raise_already_exists(
                    message=self.book_service.book_already_exists_msg,
                    author_id=author_id,
                    book_code=item.book_code,
                    existing_author_id=book_with_same_code.author_id,
                )

            await self.book_service.create_or_restore(
                author_id,
                BookCreateRequest(
                    book_code=item.book_code,
                    title=item.title,
                ),
            )

        for book in existing_books:
            if book.book_code not in target_codes:
                await self.book_service.soft_delete(book.id)

    async def create_author_with_books(self, data: AuthorAddRequest) -> None:
        author = await self.author_service.create_or_restore(data)
        for item in data.books:
            await self.book_service.create_or_restore(
                author.id,
                BookCreateRequest(
                    book_code=item.book_code,
                    title=item.title,
                ),
            )

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self.author_service.get_active_by_id_or_raise(author_id)
        books = await self.book_service.get_by_author_id(author_id)
        return Author(
            id=author.id,
            author_code=author.author_code,
            first_name=author.first_name,
            last_name=author.last_name,
            books=books,
        )

    async def get_all_authors_with_books(self, limit: int, offset: int) -> AuthorsPage:
        authors, total = await self.author_service.get_page(limit, offset)
        if not authors:
            return AuthorsPage(
                items=[],
                total=total,
                limit=limit,
                offset=offset,
            )

        author_ids = [author.id for author in authors]
        books = await self.book_service.get_orm_by_author_ids(author_ids)

        books_by_author_id = defaultdict(list)
        for book in books:
            books_by_author_id[book.author_id].append(
                {
                    "id": book.id,
                    "book_code": book.book_code,
                    "title": book.title,
                }
            )

        items: list[Author] = []
        for author in authors:
            items.append(
                Author(
                    id=author.id,
                    author_code=author.author_code,
                    first_name=author.first_name,
                    last_name=author.last_name,
                    books=books_by_author_id.get(author.id, []),
                )
            )

        return AuthorsPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def del_author_with_books(self, author_id: int) -> None:
        author = await self.author_service.get_active_by_id_or_raise(author_id)
        await self.book_service.soft_delete_by_author(author_id)
        await self.author_service.soft_delete(author_id)
        self.logger.info("author_deleted", author_id=author.id)

    async def update_author_with_books(self, author_id: int, data: AuthorPatch) -> None:
        author = await self.author_service.get_active_by_id_or_raise(author_id)
        author_data = data.model_dump(exclude_unset=True, exclude_none=True, exclude={"books"})
        if author_data:
            await self.author_service.update(author_id, data)

        if data.books is None:
            return

        await self._sync_books(author_id, data.books)
        self.logger.info("author_updated", author_id=author.id)
