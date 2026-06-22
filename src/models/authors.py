from typing import List

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class AuthorsOrm(Base):
    __tablename__ = "authors"
    __table_args__ = (
        Index(
            "uq_authors_author_code_active",
            "author_code",
            unique=True,
        ),
    )

    author_code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    books: Mapped[List["BooksOrm"]] = relationship(
        "BooksOrm",
        back_populates="author",
        cascade="all, delete-orphan",
    )
