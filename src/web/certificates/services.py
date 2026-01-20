import json
import secrets
import string
from datetime import date, datetime, timezone, timedelta

from aiokafka import AIOKafkaProducer
from starlette.requests import Request

import settings
from core.helpers import is_cert_expired
from database.models import Certificates
from database.models.certificates import Status

ALPHABET = string.digits


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


def hide_phone(phone: str) -> str:
    phone = phone.strip()
    z_ln_phone = len(phone) - 3
    return '*'*z_ln_phone + (phone or '')[-3:]


def hide_cert_sentitive_info(cert: Certificates) -> None:
    cert.phone = hide_phone(cert.phone)
    cert.name = cert.name[0] + '******' if cert.name else None
    cert.last_name = cert.last_name[0] + '******' if cert.last_name else None
    cert.transactions = []


def generate_secure_code(length: int = 4) -> str:
    return ''.join(secrets.choice(ALPHABET) for _ in range(length))


def public_base_url(request: Request) -> str:
    proto = request.headers.get("x-forwarded-proto") or "https"
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if proto and host:
        return f"{proto}://{host}".rstrip("/")
    return str(request.base_url).rstrip("/")


def get_telegram_text(cert: Certificates, request: Request) -> str:
    base = public_base_url(request)
    link = f"{base}/certificates/{cert.id}"
    return settings.TELEGRAM_TEXT_TEMPLATE.format(
        cert_code=cert.code,
        amount=cert.amount,
        phone=hide_phone(cert.phone),
        expire_date=(
            (cert.created_at + timedelta(days=cert.period)).strftime("%Y-%m-%d")
            if not cert.indefinite
            else "неограничен"
        ),
        link=link,
    )


async def send_certificate_charged_event(
    producer: AIOKafkaProducer,
    *,
    cert_id: str,
    tran_id: int,
    cert_code: str,
    charge_sum: float,
    confirm_code: str,
    phone: str,
):
    payload = {
        'event': 'CERTIFICATE_CHARGED',
        'cert_id': cert_id,
        'tran_id': tran_id,
        'cert_code': cert_code,
        'charge_sum': charge_sum,
        'confirm_code': confirm_code,
        'phone': phone,
        'ts': datetime.now(timezone.utc).isoformat(),
    }

    await producer.send_and_wait(
        topic=settings.KAFKA_SMS_TOPIC,
        value=json.dumps(payload).encode('utf-8'),
        key=cert_id.encode('utf-8'),
    )



async def send_telegram_msg_event(
    producer: AIOKafkaProducer,
    *,
    chat_id: int,
    image_url: str,
    text: str
):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'image_url': image_url,
    }

    await producer.send_and_wait(
        topic=settings.KAFKA_TELEGRAM_TOPIC,
        value=json.dumps(payload).encode('utf-8'),
        key=str(chat_id).encode('utf-8'),
    )
