import sqlalchemy as sa
from sqlalchemy.orm import relationship

from database.session import BaseModel


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

    cert = relationship(
        'Certificates',
        back_populates='transactions',
        lazy='selectin',
        passive_deletes=True,
    )
