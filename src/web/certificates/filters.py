from datetime import date

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from database.models import Certificates


class CertFilter(Filter):
    id__in: list[str] | None = Field(default=None)
    code__ilike: str | None = Field(default=None)
    status__in: list[str] | None = Field(default=None)
    created_at: date | None = Field(default=None)
    created_at__gt: date | None = Field(default=None)
    created_at__gte: date | None = Field(default=None)
    created_at__lt: date | None = Field(default=None)
    created_at__lte: date | None = Field(default=None)
    used_at: date | None = Field(default=None)
    used_at__gt: date | None = Field(default=None)
    used_at__gte: date | None = Field(default=None)
    used_at__lt: date | None = Field(default=None)
    used_at__lte: date | None = Field(default=None)
    period__gte: int | None = Field(default=None)
    period__lte: int | None = Field(default=None)
    amount__gte: int | None = Field(default=None)
    amount__lte: int | None = Field(default=None)
    phone__ilike: str | None = Field(default=None)
    last_name__ilike: str | None = Field(default=None)

    class Constants(Filter.Constants):
        model = Certificates
