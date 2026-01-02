from datetime import datetime, date

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from core.helpers import is_cert_expired
from database.models import Certificates
from database.models.certificates import Type


class ErrorSaveToDatabase(Exception):
    pass


async def update_cert_in_db(
    cert: Certificates, **update_data: dict
) -> Certificates:
    for field, value in update_data.items():
        setattr(cert, field, value)
    return cert

def set_actual_status(cert: Certificates) -> bool:
    if cert.status in [Type.CANCELLED, Type.USED]:
        return False

    initial_status = cert.status

    if is_cert_expired(cert):
        cert.status = Type.EXPIRED
    else:
        cert.status = Type.ACTIVE

    if cert.amount <= 0:
        cert.status = Type.USED
        cert.used_at = date.today()

    return cert.status != initial_status


