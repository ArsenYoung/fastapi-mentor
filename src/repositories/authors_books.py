from sqlalchemy import select, update

from src.mappers.authors_books import build_author_response
from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.base import BaseRepository
from src.schemas.authors import Author, AuthorAddRequest, AuthorPatch


class AuthorsBooksRepository(BaseRepository):
    def __init__(self, session):
        self.session = session

    async def get_author(self, author_id: int) -> Author | None:
        author = await self.session.execute(
            select(AuthorsOrm).filter_by(
                id=author_id,
                is_deleted=False
            ))
        author_response = author.scalar_one_or_none()
        return author_response

    async def create_author_with_books(self, data: AuthorAddRequest) -> None:
        author = AuthorsOrm(
            first_name=data.first_name,
            last_name=data.last_name
        )
        self.session.add(author)
        await self.session.flush()

        for item in data.books:
            book = BooksOrm(
                author_id=author.id,
                title=item.title,
            )
            self.session.add(book)

    async def get_author_with_books(self, author_id: int) -> Author | None:
        author = await self.get_author(author_id)

        if author is None:
            return None
        
        books_data = await self.session.execute(
            select(BooksOrm).filter_by(
                author_id=author.id
            ))
        
        books = books_data.scalars().all()

        return build_author_response(author, books)   

    async def del_author_with_books(self, author_id: int) -> bool:
        author = await self.get_author(author_id)

        if author is None:
            return False
        
        await self.session.execute(
            update(AuthorsOrm)
            .filter_by(id=author.id)
            .values(is_deleted=True)
        )

        await self.session.execute(
            update(BooksOrm)
            .filter_by(author_id=author_id)
            .values(is_deleted=True)
        )

        return True

    async def update_author_with_books(self, author_id: int, data: AuthorPatch) -> bool:
        author = await self.get_author(author_id)

        if author is None:
            return False
        
        author_data = data.model_dump(
            exclude_unset=True,
            exclude={"books"},
        )

        if author_data:
            await self.session.execute(
                update(AuthorsOrm)
                .filter_by(id=author_id)
                .values(**author_data)
            )

        if data.books is not None:
            for item in data.books:
                await self.session.execute(
                    update(BooksOrm)
                    .filter_by(id=item.id)
                    .values(title=item.title)
                )

        return True


