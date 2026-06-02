from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class AuthorsOrm(Base):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    books: Mapped[list["BooksOrm"]] = relationship(
        "BooksOrm",
        back_populates="author",
        cascade="all, delete-orphan",
    )
