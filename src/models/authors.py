from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class AuthorsOrm(Base):
    __tablename__ = "authors"
    __table_args__ = (
        UniqueConstraint(
            "first_name", 
            "last_name",
            name="uq_authors_first_name_last_name"
        ),
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    books: Mapped[list["BooksOrm"]] = relationship(
        "BooksOrm",
        back_populates="author",
        cascade="all, delete-orphan",
    )
