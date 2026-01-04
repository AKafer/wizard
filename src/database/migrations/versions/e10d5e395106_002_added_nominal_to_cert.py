"""002_added_nominal_to_cert

Revision ID: e10d5e395106
Revises: e861fb8e2b0e
Create Date: 2026-01-04 09:31:00.786594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e10d5e395106'
down_revision: Union[str, Sequence[str], None] = 'e861fb8e2b0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('certificates', sa.Column('nominal', sa.Float(), nullable=True))
    op.alter_column('certificates', 'description',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('certificates', 'employee',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('certificates', 'employee',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.alter_column('certificates', 'description',
               existing_type=sa.TEXT(),
               nullable=False)
    op.drop_column('certificates', 'nominal')
