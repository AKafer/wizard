from datetime import date

from core.helpers import is_cert_expired
from database.models import Certificates
from database.models.certificates import Status


class ErrorSaveToDatabase(Exception):
    pass


async def update_cert_in_db(
    cert: Certificates, **update_data: dict
) -> Certificates:
    for field, value in update_data.items():
        setattr(cert, field, value)
    return cert


def set_actual_status(cert: Certificates) -> bool:
    if cert.status in [Status.CANCELLED, Status.USED]:
        return False

    initial_status = cert.status

    if is_cert_expired(cert):
        cert.status = Status.EXPIRED
    else:
        cert.status = Status.ACTIVE

    if cert.amount <= 0:
        cert.status = Status.USED
        cert.used_at = date.today()

    return cert.status != initial_status
