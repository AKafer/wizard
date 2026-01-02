from datetime import date
from typing import Any

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field
from sqlalchemy import Select, select
from sqlalchemy.orm import Query as OrmQuery

from database.models import Certificates, User


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
    phone_number__ilike: str | None = Field(default=None)
    last_name__ilike: str | None = Field(default=None)

    class Constants(Filter.Constants):
        model = Certificates
        join_relationships = ["user"]

    @property
    def filtering_fields(self) -> Any:
        fields = self.dict(
            exclude_none=True,
            exclude_unset=True,
            exclude={
                'phone_number__ilike',
                'last_name__ilike',
            },
        )

        fields.pop(self.Constants.ordering_field_name, None)
        return fields.items()

    def filter(self, query: OrmQuery | Select) -> OrmQuery | Select | None:
        need_join = self.phone_number__ilike is not None or self.last_name__ilike is not None
        if need_join:
            query = query.join(Certificates.user)

        if self.phone_number__ilike is not None:
            phone = self.phone_number__ilike.strip()
            query = query.where(User.phone_number.ilike(f'%{phone}%'))
        if self.last_name__ilike is not None:
            last_name = self.last_name__ilike.strip()
            query = query.where(User.last_name.ilike(f'%{last_name}%'))
        return super().filter(query)
