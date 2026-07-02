from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class BooksOrm(Base):
    __tablename__ = "books"

    __table_args__ = (
        Index(
            "uq_books_book_code_active",
            "book_code",
            unique=True,
            postgresql_where=text("is_deleted = False"),
        ),
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    author: Mapped["AuthorsOrm"] = relationship(
        back_populates="books",
        passive_deletes=True,
    )
