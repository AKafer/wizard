from enum import Enum
import sqlalchemy as sa
import ulid
from sqlalchemy.orm import relationship

from database.session import BaseModel

class Certificates(BaseModel):
    __tablename__ = 'certificates'

    class Type(str, Enum):
        ACTIVE = 'ACTIVE'
        USED = 'USED'
        EXPIRED = 'EXPIRED'
        CANCELLED = 'CANCELLED'

    id = sa.Column(sa.String(26), primary_key=True, default=lambda: str(ulid.ULID()))
    code = sa.Column(sa.String(64), unique=True, nullable=False) # human-readable unique code
    user_id = sa.Column(
        sa.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    amount = sa.Column(sa.Float, nullable=False)
    description = sa.Column(sa.Text, nullable=False)
    employee = sa.Column(sa.String(128), nullable=False)
    check_amount = sa.Column(sa.Float, nullable=True)

    status = sa.Column(
        sa.Enum(Type, name='status_enum'),
        nullable=False,
        server_default=Type.ACTIVE,
    )
    created_at = sa.Column(sa.Date, nullable=True)
    used_at = sa.Column(sa.Date, nullable=True)
    indefinite = sa.Column(sa.Boolean, nullable=False, default=True)
    period = sa.Column(sa.Integer, nullable=True)


    user = relationship(
        'User',
        back_populates='certificates',
        lazy='selectin',
        passive_deletes=True
    )
