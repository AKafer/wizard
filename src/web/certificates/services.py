import json
from datetime import date, datetime, timezone

from aiokafka import AIOKafkaProducer

import settings
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


def hide_cert_sentitive_info(cert: Certificates) -> None:
    cert.phone = '*********' + (cert.phone or '')[-3:]
    cert.name = cert.name[0] + '******' if cert.name else None
    cert.last_name = cert.last_name[0] + '******' if cert.last_name else None
    cert.transactions = []


async def send_certificate_charged_event(
    producer: AIOKafkaProducer,
    *,
    cert_id: str,
    cert_code: str,
    charge_sum: float,
    new_amount: int,
    status: str,
):
    payload = {
        'event': 'CERTIFICATE_CHARGED',
        'cert_id': cert_id,
        'cert_code': cert_code,
        'charge_sum': charge_sum,
        'new_amount': new_amount,
        'status': status,
        'ts': datetime.now(timezone.utc).isoformat(),
    }

    await producer.send_and_wait(
        topic=settings.KAFKA_SMS_TOPIC,
        value=json.dumps(payload).encode('utf-8'),
        key=cert_id.encode('utf-8'),
    )
