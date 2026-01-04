from enum import Enum

import sqlalchemy as sa
import ulid
from sqlalchemy.orm import relationship

from database.session import BaseModel


class Status(str, Enum):
    ACTIVE = 'ACTIVE'
    USED = 'USED'
    EXPIRED = 'EXPIRED'
    CANCELLED = 'CANCELLED'


class Certificates(BaseModel):
    __tablename__ = 'certificates'

    id = sa.Column(
        sa.String(26), primary_key=True, default=lambda: str(ulid.ULID())
    )
    code = sa.Column(sa.String(64), unique=True, nullable=False)
    nominal = sa.Column(sa.Float, nullable=True)
    amount = sa.Column(sa.Float, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    employee = sa.Column(sa.String(128), nullable=True)
    check_amount = sa.Column(sa.Float, nullable=True)
    status = sa.Column(
        sa.Enum(Status, name='status_enum'),
        nullable=False,
        server_default=Status.ACTIVE,
    )
    created_at = sa.Column(sa.Date, nullable=True)
    used_at = sa.Column(sa.Date, nullable=True)
    indefinite = sa.Column(sa.Boolean, nullable=False, default=True)
    period = sa.Column(sa.Integer, nullable=True)
    name = sa.Column(sa.String(256), nullable=True)
    last_name = sa.Column(sa.String(256), nullable=True)
    phone = sa.Column(sa.String(256), nullable=False)

    transactions = relationship(
        'Transactions',
        back_populates='cert',
        lazy='selectin',
        cascade='all, delete, delete-orphan',
        single_parent=True,
    )
