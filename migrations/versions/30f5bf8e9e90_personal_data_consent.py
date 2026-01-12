"""personal data consent

Revision ID: 30f5bf8e9e90
Revises: 0fe4af0b26e5
Create Date: 2026-01-12 18:31:23.202268

"""
import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30f5bf8e9e90'
down_revision: Union[str, Sequence[str], None] = '0fe4af0b26e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "personal_data_consents",
        sa.Column("telegram_id", sa.BigInteger, primary_key=True),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consent_version", sa.Date, nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
