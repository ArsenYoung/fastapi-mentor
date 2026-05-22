from src.db import get_session
from src.exceptions import ObjectAlreadyExists, ObjectNotFound
from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.repositories.authors import AuthorsRepository
from src.repositories.books import BooksRepository
from src.schemas.authors import Author, AuthorAddRequest
from src.schemas.books import Book, BookAdd


class AuthorsBooksService():
    def __init__(self, session):
        self.authors_repo = AuthorsRepository(session)
        self.books_repo = BooksRepository(session)
    
    async def create_author_with_books(self, data: AuthorAddRequest):
        is_author_exists = await self.authors_repo.get_one_or_none(name=data.name)
        if is_author_exists:
            raise ObjectAlreadyExists
        author_res = await self.authors_repo.add(data, exclude={"books"})
        books_data = [
            BookAdd(author_id=author_res.id, title=item.title)
            for item in data.books
        ]
        await self.books_repo.add_bulk(books_data)

    async def get_author_with_books(self, author_id: int):
        author_res = await self.authors_repo.get_one_or_none(id=author_id)
        if author_res is None:
            raise ObjectNotFound
        books_res = await self.books_repo.get_all(author_id=author_id)
        return build_author_response(author_res, books_res)
    
async def get_authors_books_service():
    async with get_session() as session:
        yield AuthorsBooksService(session)

def build_author_response(author: AuthorsOrm, books: list[BooksOrm]):
    return Author.model_validate({
        "id": author.id,
        "name": author.name,
        "books": [Book.model_validate(book) for book in books]
    })
