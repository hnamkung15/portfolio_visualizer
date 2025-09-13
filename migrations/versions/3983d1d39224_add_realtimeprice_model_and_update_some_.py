"""Add RealTimePrice model and update some nullable field

Revision ID: 3983d1d39224
Revises: df4f47d9f09f
Create Date: 2025-09-04 21:49:43.687478

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3983d1d39224"
down_revision: Union[str, Sequence[str], None] = "df4f47d9f09f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tickers",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("symbol", sa.VARCHAR(length=20), nullable=False),
        sa.Column("name", sa.VARCHAR(length=100), nullable=True),
        sa.Column("exchange", sa.VARCHAR(length=50), nullable=True),
        sa.Column("currency", sa.VARCHAR(length=10), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol"),
    )
    op.create_table(
        "prices",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("ticker_id", sa.INTEGER(), nullable=False),
        sa.Column("date", sa.DATE(), nullable=True),
        sa.Column("close", sa.NUMERIC(precision=12, scale=4), nullable=True),
        sa.Column("open", sa.NUMERIC(precision=12, scale=4), nullable=True),
        sa.Column("high", sa.NUMERIC(precision=12, scale=4), nullable=True),
        sa.Column("low", sa.NUMERIC(precision=12, scale=4), nullable=True),
        sa.Column("volume", sa.NUMERIC(precision=20, scale=2), nullable=True),
        sa.ForeignKeyConstraint(
            ["ticker_id"],
            ["tickers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "realtime_prices",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("ticker_id", sa.INTEGER(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("price", sa.NUMERIC(precision=12, scale=4), nullable=True),
        sa.ForeignKeyConstraint(["ticker_id"], ["tickers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sync_log",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sync_log")
    op.drop_table("realtime_prices")
    op.drop_table("prices")
    op.drop_table("tickers")
