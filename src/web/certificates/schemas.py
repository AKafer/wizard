from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_serializer

SERVER_TZ = ZoneInfo('Europe/Moscow')


class Transaction(BaseModel):
    time: datetime | None
    amount: float
    sms_id: str | None
    sms_sent: bool | None
    sms_error: str | None

    @field_serializer('time')
    def serialize_time(self, dt: datetime):
        return dt.astimezone(SERVER_TZ).isoformat()

    model_config = {'from_attributes': True}


class Certificate(BaseModel):
    id: str
    code: str
    nominal: float
    amount: float
    description: str
    employee: str
    check_amount: float | None
    status: str
    created_at: date | None
    used_at: date | None
    indefinite: bool
    period: int | None
    name: str
    last_name: str
    phone: str

    model_config = {'from_attributes': True}


class CertificateAmount(BaseModel):
    nominal: float
    amount: float
    code: str
    description: str
    status: str
    created_at: date | None
    used_at: date | None
    period: int | None
    name: str | None
    last_name: str | None
    phone: str
    transactions: list[Transaction]

    model_config = {'from_attributes': True}


class CertificateCreate(BaseModel):
    nominal: float
    description: str
    employee: str
    check_amount: float | None
    status: str
    created_at: date | None
    indefinite: bool
    period: int | None
    name: str | None
    last_name: str | None
    phone: str


class CertificateUpdate(BaseModel):
    amount: float | None = None
    description: str | None = None
    employee: str | None = None
    check_amount: float | None = None
    indefinite: bool | None = None
    period: int | None = None
    name: str | None = None
    last_name: str | None = None
    phone: str | None = None
