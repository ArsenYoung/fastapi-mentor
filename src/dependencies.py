from src.db import get_session
from src.services.authors_books import AuthorsBooksService


async def get_authors_books_service():
    async with get_session() as session:
        yield AuthorsBooksService(session)
