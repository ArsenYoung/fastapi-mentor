from collections import defaultdict
from dataclasses import dataclass
from src.mappers.authors_books import build_author_response
from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository
from src.schemas.authors import Author, AuthorAddRequest, AuthorPatch

@dataclass(slots=True)
class UpdateAuthorsResult:
    author_found: bool
    books_found: bool

class AuthorsBooksRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_author(self, author_id: int) -> Author | None:
        return await self.fetch_active_one(AuthorsOrm, id=author_id)

    async def create_author_with_books(self, data: AuthorAddRequest) -> None:
        author = await self.insert_instance(
            AuthorsOrm(
                first_name=data.first_name,
                last_name=data.last_name,
            )
        )
        for item in data.books:
            await self.insert_instance(
                BooksOrm(
                    author_id=author.id,
                    title=item.title,
                )
            )

    async def get_author_with_books(self, author_id: int) -> Author | None:
        author = await self.get_author(author_id)
        if author is None:
            return None
        books = await self.fetch_active_all(
            BooksOrm,
            author_id=author.id,
        )
        return build_author_response(author, books)
    
    async def get_all_authors_with_books(self, limit: int, offset: int) -> tuple[list[Author], int]:
        authors, total = await self.fetch_active_page(
            AuthorsOrm,
            limit=limit,
            offset=offset,
            order_by=AuthorsOrm.id
        )
        if not authors:
            return [], total
        
        authors_ids = [author.id for author in authors]
        books = await self.fetch_active_in(
            BooksOrm,
            BooksOrm.author_id,
            authors_ids,
            order_by=BooksOrm.id
        )
        books_by_author_id: dict[int, list[BooksOrm]] = defaultdict(list)
        for book in books:
            books_by_author_id[book.author_id].append(book)
        result = [build_author_response(author, books_by_author_id[author.id]) for author in authors]
        return result, total

    async def del_author_with_books(self, author_id: int) -> bool:
        author = await self.get_author(author_id)
        if author is None:
            return False
        await self.soft_delete_where(
            AuthorsOrm,
            id=author.id,
        )
        await self.soft_delete_where(
            BooksOrm,
            author_id=author.id,
        )
        return True

    async def update_author_with_books(self, author_id: int, data: AuthorPatch) -> bool:
        author = await self.get_author(author_id)
        if author is None:
            return UpdateAuthorsResult(
                author_found=False,
                books_found=False,
            )
        await self.update_where(
            AuthorsOrm,
            data.model_dump(
                exclude_unset=True,
                exclude={"books"},
            ),
            id=author_id,
        )
        if data.books is not None:
            for item in data.books:
                exists_book = await self.fetch_active_one(
                    BooksOrm,
                    id=item.id,
                    author_id=author_id,
                )
                if exists_book is None:
                    return UpdateAuthorsResult(
                        author_found=True,
                        books_found=False,
                    )
                
                await self.update_where(
                    BooksOrm,
                    item.model_dump(exclude_unset=True),
                    id=item.id,
                )

        return UpdateAuthorsResult(
            author_found=True,
            books_found=True,
        )


