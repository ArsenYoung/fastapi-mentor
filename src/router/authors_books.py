from fastapi import APIRouter, Body

from src.db import get_session
from src.repositories.authors import AuthorsRepository
from src.repositories.books import BooksRepository
from src.schemas.authors import AuthorAddRequest
from src.schemas.books import BookAdd


router = APIRouter(prefix="/authors", tags=["Авторы и книги"])


@router.post("", summary="Добавить автора и его книги")
async def post_author_with_books(
    data: AuthorAddRequest = Body(openapi_examples={
            "1": {
                "summary": "Лев Толстой",
                "value": {
                    "name": "Лев Толстой",
                    "books": [
                        {
                            "title": "Война и Мир"
                        },
                        {
                            "title": "Воскресенье"
                        },
                    ],
                },
            },
        }
    )
):
    async with get_session() as session:
        authors_repo = AuthorsRepository(session)
        author_res = await authors_repo.add(data, exclude={"books"})
        
        books_repo = BooksRepository(session)
        books_data = [
            BookAdd(author_id=author_res.id, title=item.title)
            for item in data.books
        ]
        books_res = await books_repo.add_bulk(books_data)

        return books_res
    # books_query = insert(BooksOrm).values(**books_data.model_dump()) response_model=AuthorRead, 
