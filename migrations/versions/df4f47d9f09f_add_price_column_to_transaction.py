"""add price column to transaction

Revision ID: df4f47d9f09f
Revises: 88212f8d928a
Create Date: 2025-08-06 12:07:04.395072

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "df4f47d9f09f"
down_revision: Union[str, Sequence[str], None] = "88212f8d928a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transactions", "price")
