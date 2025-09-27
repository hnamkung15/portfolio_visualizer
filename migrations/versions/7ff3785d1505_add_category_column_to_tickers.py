"""add_category_column_to_tickers

Revision ID: 7ff3785d1505
Revises: cd33bd6bf509
Create Date: 2025-09-26 17:11:36.018202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ff3785d1505'
down_revision: Union[str, Sequence[str], None] = 'cd33bd6bf509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add category column to tickers table
    op.add_column('tickers', sa.Column('category', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove category column from tickers table
    op.drop_column('tickers', 'category')
