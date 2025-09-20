"""add last_data_sync column to tickers

Revision ID: cd33bd6bf509
Revises: 58695790ff5b
Create Date: 2025-09-19 18:28:48.531357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd33bd6bf509'
down_revision: Union[str, Sequence[str], None] = '3983d1d39224'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add last_data_sync column to tickers table
    op.add_column('tickers', sa.Column('last_data_sync', sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove last_data_sync column from tickers table
    op.drop_column('tickers', 'last_data_sync')
