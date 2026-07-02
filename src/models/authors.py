from sqlalchemy import Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class AuthorsOrm(Base):
    __tablename__ = "authors"

    __table_args__ = (
        Index(
            "uq_authors_author_code_active",
            "author_code", 
            unique=True,
            postgresql_where=text("is_deleted = False"),
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
    books: Mapped[set["BooksOrm"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        collection_class=set,
        primaryjoin="and_(AuthorsOrm.id == BooksOrm.author_id, BooksOrm.is_deleted.is_(False))",
        lazy="selectin",
    )
