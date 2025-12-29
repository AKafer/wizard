from datetime import date
from uuid import UUID

from pydantic import BaseModel

class User(BaseModel):
    name: str
    last_name: str
    phone_number: str

    model_config = {"from_attributes": True}



class Certificate(BaseModel):
    user_id: UUID
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
    user: User

    model_config = {"from_attributes": True}


class CertificateAmount(BaseModel):
    amount: float
    description: str
    status: str
    created_at: date | None
    period: int | None
    user: User

    model_config = {"from_attributes": True}


class CertificateCreate(BaseModel):
    user_id: str
    amount: float
    description: str
    employee: str
    check_amount: float | None
    status: str
    created_at: date | None
    indefinite: bool
    period: int | None


class CertificateUpdate(BaseModel):
    amount: float | None = None
    description: str | None = None
    employee: str | None = None
    check_amount: float | None = None
    status: str | None = None
    used_at: date | None = None
    indefinite: bool | None = None
    period: int | None = None
