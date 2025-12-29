import uuid
from datetime import datetime, date, time

from fastapi_users import schemas
from pydantic import EmailStr, Field, BaseModel


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

    model_config = {"from_attributes": True}


class UserRead(schemas.BaseUser[uuid.UUID]):
    email: EmailStr
    name: str
    last_name: str
    father_name: str | None
    telegram_id: str | None
    phone_number: str | None
    created_at: datetime
    updated_at: datetime | None
    is_active: bool = Field(True, exclude=True)
    is_verified: bool = Field(False, exclude=True)
    is_superuser: bool = Field(False, exclude=True)
    date_of_birth: datetime | None
    gender: str | None = None
    certificates: list[Certificate]



class CustomDateTime:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            if 'T' in value:
                try:
                    value = value.rstrip('Z')
                    return datetime.fromisoformat(value)
                except Exception as e:
                    raise ValueError(
                        f'Invalid datetime format: {value}'
                    ) from e
            else:
                try:
                    d = date.fromisoformat(value)
                    return datetime.combine(d, time(9, 0))
                except Exception as e:
                    raise ValueError(f'Invalid date format: {value}') from e

        raise TypeError(f'Expected a string or datetime, got {type(value)}')

    @classmethod
    def __modify_schema__(cls, field_schema: dict) -> None:
        """
        This method updates the JSON schema for the custom field so that
        OpenAPI documentation can correctly represent it.
        """
        field_schema.update(
            type='string',
            format='date-time',
            description=(
                "A datetime string in ISO format. Date-only strings in 'YYYY-MM-DD' format "
                'are also accepted; in that case, the time defaults to 00:00:00.'
            ),
        )


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    name: str
    last_name: str
    father_name: str | None = None
    telegram_id: str | None = None
    phone_number: str | None = None
    is_active: bool = Field(True, exclude=True)
    is_verified: bool = Field(False, exclude=True)
    is_superuser: bool = Field(False, exclude=True)
    date_of_birth: datetime | None = None
    gender: str | None = None



class UserUpdate(schemas.BaseUserUpdate):
    email: EmailStr | None = None
    password: str | None = None
    name: str | None = None
    last_name: str | None = None
    father_name: str | None = None
    telegram_id: str | None = None
    phone_number: str | None = None
    is_active: bool = Field(True, exclude=True)
    is_verified: bool = Field(False, exclude=True)
    is_superuser: bool = Field(False, exclude=True)
    date_of_birth: datetime | None
    gender: str | None = None


class UserListRead(schemas.BaseUser[uuid.UUID]):
    email: EmailStr
    name: str
    last_name: str
    father_name: str | None
    telegram_id: str | None
    phone_number: str | None
    is_active: bool = Field(True, exclude=True)
    is_verified: bool = Field(False, exclude=True)
    is_superuser: bool = Field(False, exclude=True)
    date_of_birth: datetime | None
    gender: str | None = None


class UserListReadLight(schemas.BaseUser[uuid.UUID]):
    name: str
    last_name: str
    father_name: str | None
