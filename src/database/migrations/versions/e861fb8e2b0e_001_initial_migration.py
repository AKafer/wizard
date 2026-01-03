"""001_initial_migration

Revision ID: e861fb8e2b0e
Revises: 
Create Date: 2026-01-03 05:26:42.436703

"""
from typing import Sequence, Union

import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e861fb8e2b0e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('certificates',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('employee', sa.String(length=128), nullable=False),
    sa.Column('check_amount', sa.Float(), nullable=True),
    sa.Column('status', sa.Enum('ACTIVE', 'USED', 'EXPIRED', 'CANCELLED', name='status_enum'), server_default='ACTIVE', nullable=False),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.Column('used_at', sa.Date(), nullable=True),
    sa.Column('indefinite', sa.Boolean(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('last_name', sa.String(length=256), nullable=True),
    sa.Column('phone', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('user',
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('name', sa.String(length=320), nullable=False),
    sa.Column('last_name', sa.String(length=320), nullable=False),
    sa.Column('father_name', sa.String(length=320), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    op.execute("""
            CREATE SEQUENCE IF NOT EXISTS certificates_code_seq START WITH 1 INCREMENT BY 1;
        """)

    op.execute("""
               CREATE
               OR REPLACE FUNCTION certificates_set_code()
            RETURNS trigger AS $$
            DECLARE
               seq_val bigint;
               BEGIN
                IF
               NEW.code IS NULL OR NEW.code = '' THEN
                    seq_val := nextval('certificates_code_seq');
                    NEW.code
               := 'AN-' || lpad(seq_val::text, 6, '0');
               END IF;

               RETURN NEW;
               END;
            $$
               LANGUAGE plpgsql;
               """)

    op.execute("""
               CREATE TRIGGER trg_certificates_set_code
                   BEFORE INSERT
                   ON certificates
                   FOR EACH ROW
                   EXECUTE FUNCTION certificates_set_code();
               """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_certificates_set_code ON certificates;")
    op.execute("DROP FUNCTION IF EXISTS certificates_set_code();")
    op.execute("DROP SEQUENCE IF EXISTS certificates_code_seq;")
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('certificates')
