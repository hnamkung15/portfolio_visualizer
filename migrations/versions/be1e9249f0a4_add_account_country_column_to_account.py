"""add account_country column to account

Revision ID: be1e9249f0a4
Revises: 24e4e367a76e
Create Date: 2025-08-03 01:18:46.356679

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "be1e9249f0a4"
down_revision: Union[str, Sequence[str], None] = "24e4e367a76e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    account_country_enum = sa.Enum("KOR", "US", name="accountcountry")
    account_country_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "accounts",
        sa.Column(
            "account_country", account_country_enum, nullable=False, server_default="US"
        ),
    )


def downgrade() -> None:
    op.drop_column("accounts", "account_country")
    sa.Enum(name="accountcountry").drop(op.get_bind(), checkfirst=True)
