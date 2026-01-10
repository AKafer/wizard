import asyncio
import logging
from datetime import datetime, time, timedelta

from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.models import Certificates, Transactions
from database.models.certificates import Status
from database.models.transactions import StatusTran
from database.session import Session
from web.certificates.services import set_actual_status

logger = logging.getLogger('wizard')


async def refresh_certificates(session: AsyncSession) -> int:
    query = select(Certificates).filter(
        Certificates.status == Status.ACTIVE,
        Certificates.status == Status.EXPIRED,
        Certificates.indefinite == False,
    )
    result = await session.execute(query)
    actual_certs = result.scalars().all()

    updated_certs = 0
    for cert in actual_certs:
        if set_actual_status(cert):
            updated_certs += 1

    await session.commit()
    return updated_certs


async def actualize_certificates():
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


async def cancel_expired_transactions():
    while True:
        try:
            async with Session() as session:
                cutoff = func.timezone('utc', func.now()) - text(
                    f"interval '{settings.TRANSACTION_VALID_TIME} minutes'"
                )

                stmt = (
                    update(Transactions)
                    .where(Transactions.status == StatusTran.OPENED)
                    .where(Transactions.time < cutoff)
                    .values(status=StatusTran.CANCELLED)
                )

                result = await session.execute(stmt)
                await session.commit()

                updated = result.rowcount or 0
                logger.info(
                    'Expired transactions cancelled. Updated=%s', updated
                )

        except Exception as e:
            logger.exception('Error cancelling expired transactions: %s', e)

        await asyncio.sleep(settings.TRANSACTION_CHECK_INTERVAL)
