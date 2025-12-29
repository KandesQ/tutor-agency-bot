"""create tutors table

Revision ID: 279fd2ca1f2e
Revises: 
Create Date: 2025-12-27 01:10:11.079144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '279fd2ca1f2e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tutors",
        sa.Column("account_id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("surname", sa.String(100), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("fathers_name", sa.String(100), nullable=True),
        sa.Column("birthday_date", sa.Date, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
