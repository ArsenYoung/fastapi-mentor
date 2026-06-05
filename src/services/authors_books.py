from collections import defaultdict

from sqlalchemy.exc import IntegrityError

from src.exceptions.already_exists_exception import AlreadyExistsException
from src.exceptions.object_not_found_exception import ObjectNotFoundException
from src.mappers.authors_books import build_author_response
from src.repositories.authors_books import AuthorsBooksRepository
from src.schemas.authors import Author, AuthorAddRequest, AuthorPatch, AuthorsPage


class AuthorsBooksService:
    def __init__(self, repo: AuthorsBooksRepository):
        self.repo = repo

    async def create_author_with_books(self, data: AuthorAddRequest) -> None:
        author = await self.repo.get_author_by_code(data.author_code)

        if author is None:
            try:
                author = await self.repo.insert_author(
                    author_code=data.author_code,
                    first_name=data.first_name,
                    last_name=data.last_name,
                )
            except IntegrityError as exc:
                raise AlreadyExistsException("An author with this code already exists") from exc
        elif author.is_deleted:
            await self.repo.restore_author(author.id)
            await self.repo.update_author(
                author.id,
                {
                    "author_code": data.author_code,
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                },
            )
        else:
            raise AlreadyExistsException("An author with this code already exists")

        for book in data.books:
            await self.repo.insert_book(
                author.id,
                book.book_code,
                book.title,
            )

    async def get_author_with_books(self, author_id: int) -> Author:
        author = await self.repo.get_author(author_id)
        if author is None:
            raise ObjectNotFoundException("Author not found")

        books = await self.repo.get_books_by_author(author_id)
        return build_author_response(author, books)

    async def get_all_authors_with_books(self, limit: int, offset: int) -> AuthorsPage:
        authors, total = await self.repo.get_authors_page(limit, offset)
        if not authors:
            return AuthorsPage(
                items=[],
                total=total,
                limit=limit,
                offset=offset,
            )

        author_ids = [author.id for author in authors]
        books = await self.repo.get_books_by_author_ids(author_ids)

        books_by_author_id: dict[int, list] = defaultdict(list)
        for book in books:
            books_by_author_id[book.author_id].append(book)

        items = [
            build_author_response(author, books_by_author_id.get(author.id, []))
            for author in authors
        ]

        return AuthorsPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def del_author_with_books(self, author_id: int) -> None:
        author = await self.repo.get_author(author_id)
        if author is None:
            raise ObjectNotFoundException("Author not found")

        await self.repo.soft_delete_author(author_id)
        await self.repo.soft_delete_books_by_author(author_id)

    async def update_author_with_books(self, author_id: int, data: AuthorPatch) -> None:
        author = await self.repo.get_author(author_id)
        if author is None:
            raise ObjectNotFoundException("Author not found")

        author_data = data.model_dump(
            exclude_unset=True,
            exclude={"books"},
        )
        if author_data:
            try:
                await self.repo.update_author(author_id, author_data)
            except IntegrityError as exc:
                raise AlreadyExistsException("An author with this code already exists") from exc

        if data.books is None:
            return

        for book_data in data.books:
            book = await self.repo.get_book(book_data.book_code, author_id)
            if book is None:
                raise ObjectNotFoundException("Book not found")

            values = book_data.model_dump(exclude_unset=True, exclude={"book_code"})
            if values:
                await self.repo.update_book(book_data.book_code, author_id, values)
