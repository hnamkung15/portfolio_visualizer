"""add quantity and fee column to transactions

Revision ID: 88212f8d928a
Revises: de1fe394c528
Create Date: 2025-08-06 00:25:49.955706

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "88212f8d928a"
down_revision: Union[str, Sequence[str], None] = "de1fe394c528"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("quantity", sa.Numeric(precision=12, scale=4), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("fee", sa.Numeric(precision=12, scale=2), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("transactions", "fee")
    op.drop_column("transactions", "quantity")
