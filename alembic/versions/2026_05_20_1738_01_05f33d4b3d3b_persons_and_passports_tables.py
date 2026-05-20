"""persons and passports tables

Revision ID: 05f33d4b3d3b
Revises: bd4d7f2c9a11
Create Date: 2026-05-20 17:38:01.831757

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "05f33d4b3d3b"
down_revision: Union[str, Sequence[str], None] = "bd4d7f2c9a11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=20), nullable=False),
        sa.Column("last_name", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "passports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=15), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("person_id"),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("passports")
    op.drop_table("persons")
