"""add book_code

Revision ID: add_book_code_20260605
Revises: add_author_code_20260605
Create Date: 2026-06-05 15:04:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_book_code_20260605"
down_revision: Union[str, Sequence[str], None] = "add_author_code_20260605"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "books",
        sa.Column("book_code", sa.String(length=32), nullable=True),
    )
    op.execute("UPDATE books SET book_code = 'book-' || id WHERE book_code IS NULL")
    op.alter_column("books", "book_code", nullable=False)
    op.create_index(
        "uq_books_book_code_active",
        "books",
        ["book_code"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_books_book_code_active",
        table_name="books",
        postgresql_where=sa.text("is_deleted = false"),
    )
    op.drop_column("books", "book_code")
