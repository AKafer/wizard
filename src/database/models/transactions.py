from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.session import BaseModel


class StatusTran(str, Enum):
    OPENED = 'OPENED'
    CANCELLED = 'CANCELLED'
    DONE = 'DONE'


class Transactions(BaseModel):
    __tablename__ = 'transactions'

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cert_id = sa.Column(
        sa.String(26),
        sa.ForeignKey('certificates.id', ondelete='CASCADE'),
        nullable=False,
    )
    time = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("timezone('utc', now())"),
    )
    amount = sa.Column(sa.Float, nullable=False)
    sms_id = sa.Column(sa.String(64), nullable=True)
    sms_sent = sa.Column(sa.Boolean, nullable=True)
    sms_error = sa.Column(sa.String(256), nullable=True)
    confirm_code = sa.Column(sa.String(256), nullable=True)
    status = sa.Column(
        sa.Enum(StatusTran, name='status_tran_enum'),
        nullable=False,
        server_default=StatusTran.OPENED,
    )

    cert = relationship(
        'Certificates',
        back_populates='transactions',
        lazy='selectin',
        passive_deletes=True,
    )
