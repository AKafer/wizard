"""004_added_sms_fields_to_transactions

Revision ID: c6f13e48d720
Revises: c24c37233df1
Create Date: 2026-01-04 13:41:13.207764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6f13e48d720'
down_revision: Union[str, Sequence[str], None] = 'c24c37233df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('transactions', sa.Column('sms_id', sa.String(length=64), nullable=True))
    op.add_column('transactions', sa.Column('sms_sent', sa.Boolean(), nullable=True))
    op.add_column('transactions', sa.Column('sms_error', sa.String(length=256), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('transactions', 'sms_error')
    op.drop_column('transactions', 'sms_sent')
    op.drop_column('transactions', 'sms_id')
