"""create payments table

Revision ID: 0fe4af0b26e5
Revises: 279fd2ca1f2e
Create Date: 2025-12-27 01:10:54.919998

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from models.enums import PaymentStatus

# revision identifiers, used by Alembic.
revision: str = '0fe4af0b26e5'
down_revision: Union[str, Sequence[str], None] = '279fd2ca1f2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("student_surname", sa.String(100), nullable=False),
        sa.Column("student_name", sa.String(100), nullable=False),
        sa.Column("student_fathers_name", sa.String(100), nullable=True),
        sa.Column("subject", sa.String(100), nullable=False),
        sa.Column("lesson_number", sa.Integer, nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_status", sa.Enum(PaymentStatus), nullable=False),
        sa.Column("tutor_chat_id", sa.BigInteger, nullable=False),
        sa.ForeignKeyConstraint(("tutor_chat_id",), ["tutors.chat_id"])
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
