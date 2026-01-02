import asyncio
import logging
from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.certificates import Type
from database.session import Session
from database.models import Certificates
from web.certificates.services import set_actual_status

logger = logging.getLogger('wizard')


async def refresh_certificates(session: AsyncSession) -> int:
    query = select(Certificates).filter(
        Certificates.status == Type.ACTIVE,
        Certificates.status == Type.EXPIRED,
        Certificates.indefinite == False
    )
    result = await session.execute(query)
    actual_certs = result.scalars().all()

    updated_certs = 0
    for cert in actual_certs:
        if set_actual_status(cert):
            updated_certs += 1

    await session.commit()
    return updated_certs


async def daily_job():
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), time(0, 0))
        if now >= target:
            target += timedelta(days=1)
        sleep_seconds = (target - now).total_seconds()

        await asyncio.sleep(sleep_seconds)

        try:
            async with Session() as session:
                updated = await refresh_certificates(session)
            logger.info('Certificates refreshed. Updated=%s', updated)
        except Exception as e:
            logger.exception('Error refreshing certificates: %s', e)