"""add author_code

Revision ID: add_author_code_20260605
Revises: 5f284cbc4415
Create Date: 2026-06-05 14:49:45

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_author_code_20260605"
down_revision: Union[str, Sequence[str], None] = "5f284cbc4415"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "authors",
        sa.Column("author_code", sa.String(length=32), nullable=True),
    )
    op.execute("UPDATE authors SET author_code = 'author-' || id WHERE author_code IS NULL")
    op.alter_column("authors", "author_code", nullable=False)
    op.drop_constraint("uq_authors_first_name_last_name", "authors", type_="unique")
    op.create_index(
        "uq_authors_author_code_active",
        "authors",
        ["author_code"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_authors_author_code_active",
        table_name="authors",
        postgresql_where=sa.text("is_deleted = false"),
    )
    op.create_unique_constraint(
        "uq_authors_first_name_last_name",
        "authors",
        ["first_name", "last_name"],
    )
    op.drop_column("authors", "author_code")
