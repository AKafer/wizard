"""005_add_status_to_tran

Revision ID: 8b094802a95e
Revises: c6f13e48d720
Create Date: 2026-01-10 08:47:00.412737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b094802a95e'
down_revision: Union[str, Sequence[str], None] = 'c6f13e48d720'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('certificates', sa.Column('actual_tran_id', sa.BigInteger(), nullable=True))
    op.add_column('transactions', sa.Column('confirm_code', sa.String(length=256), nullable=True))

    status_enum = sa.Enum('OPENED', 'CANCELLED', 'DONE', name='status_tran_enum')
    status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'transactions', sa.Column(
            'status',
            status_enum,
            server_default='OPENED',
            nullable=False
                  )
    )
    op.create_index(
        'ix_transactions_opened_time',
        'transactions',
        ['time'],
        unique=False,
        postgresql_where=sa.text("status = 'OPENED'")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_transactions_opened_time', table_name='transactions')
    op.drop_column('transactions', 'status')
    op.drop_column('transactions', 'confirm_code')
    op.drop_column('certificates', 'actual_tran_id')
    status_enum = sa.Enum('OPENED', 'CANCELLED', 'DONE', name='status_tran_enum')
    status_enum.drop(op.get_bind(), checkfirst=True)