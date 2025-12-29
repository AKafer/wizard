"""002_add_gender_to_user

Revision ID: d17cb85cd541
Revises: f61d9c3eb181
Create Date: 2025-12-29 11:58:23.385276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd17cb85cd541'
down_revision: Union[str, Sequence[str], None] = 'f61d9c3eb181'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('gender', sa.String(length=32), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'gender')
