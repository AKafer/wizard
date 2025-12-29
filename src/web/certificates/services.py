import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Certificates


class ErrorSaveToDatabase(Exception):
    pass


async def update_cert_in_db(
    cert: Certificates, **update_data: dict
) -> Certificates:
    for field, value in update_data.items():
        setattr(cert, field, value)
    return cert