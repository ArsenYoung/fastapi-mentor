"""books author fk cascade

Revision ID: bd4d7f2c9a11
Revises: 39838526a486
Create Date: 2026-05-20 17:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bd4d7f2c9a11"
down_revision: Union[str, Sequence[str], None] = "39838526a486"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("books_author_id_fkey", "books", type_="foreignkey")
    op.create_foreign_key(
        "books_author_id_fkey",
        "books",
        "authors",
        ["author_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("books_author_id_fkey", "books", type_="foreignkey")
    op.create_foreign_key(
        "books_author_id_fkey",
        "books",
        "authors",
        ["author_id"],
        ["id"],
    )
