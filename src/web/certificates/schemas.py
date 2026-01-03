from datetime import date
from uuid import UUID

from pydantic import BaseModel


class Certificate(BaseModel):
    id: str
    code: str
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

    model_config = {'from_attributes': True}


class CertificateCreate(BaseModel):
    amount: float
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
    status: str | None = None
    used_at: date | None = None
    indefinite: bool | None = None
    period: int | None = None
    name: str | None = None
    last_name: str | None = None
    phone: str | None = None
