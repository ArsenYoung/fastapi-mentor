from fastapi import APIRouter, Body
from sqlalchemy import insert

from src.db import get_session
from src.models.authors import AuthorsOrm
from src.models.books import BooksOrm
from src.schemas.authors import AuthorCreate


router = APIRouter(prefix="/authors", tags=["Авторы и книги"])


@router.post("", summary="Добавить автора и его книги")
async def post_author_with_books(
    data: AuthorCreate = Body(openapi_examples={
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
    author_data = data.model_dump(exclude={"books"})
    author_query = insert(AuthorsOrm).values(**author_data).returning(AuthorsOrm.id)

    async with get_session() as session:
        author_res = await session.execute(author_query)
        author_id = author_res.scalar_one()
        books_data = []
        for book in data.books:
            books_data.append({
                "author_id": author_id,
                **book.model_dump()
            })
        
        books_query = insert(BooksOrm).values(books_data)
        await session.execute(books_query)
    
    return {"status": "ok"}
    # books_query = insert(BooksOrm).values(**books_data.model_dump()) response_model=AuthorRead, 
