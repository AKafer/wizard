import asyncio
import json
import logging
import os
import random
import sys
import uuid
from logging import config as logging_config

from sqlalchemy import select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings
from core.workers import AsyncKafkaBaseWorker, AsyncKafkaWorkerRunner
from database.models import Transactions
from database.session import Session
from externals.http.mts_integration import (
    NOT_FOUND_MSG_ERROR,
    MtsAPI,
    NotCorrectPhoneNumberError,
)

logging_config.dictConfig(settings.LOGGING)
logger = logging.getLogger('wizard')


class SmsWorker(AsyncKafkaBaseWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mts = MtsAPI()

    @staticmethod
    def get_topics():
        return [settings.KAFKA_SMS_TOPIC]

    async def update_tran(self, tran_id, message_id, sent, error):
        async with Session() as session:
            query = select(Transactions).where(Transactions.id == tran_id)
            result = await session.execute(query)
            tran = result.scalar_one_or_none()
            if tran:
                tran.sms_id = message_id
                tran.sms_sent = sent
                tran.sms_error = error[0:255] if error else None
                await session.commit()

    async def check_msg_with_retry(
        self, message_id: str
    ) -> (bool | None, str | None):
        sent, error = None, None
        for attempt in range(settings.MTS_CHECK_ATTEMPTS):
            delay = min(
                settings.MTS_CHECK_BASE_DELAY * (2**attempt),
                settings.MTS_CHECK_MAX_DELAY,
            )
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)

            logger.info(
                f'attempt {attempt} for checking SMS status '
                f'for message_id {message_id}'
            )
            sent, error = await self.mts.check_message(message_id)

            if error != NOT_FOUND_MSG_ERROR:
                break

        return sent, error

    async def handle(self, message):
        body = json.loads(message.value.decode('utf-8'))
        phone = body.get('phone')
        if settings.MTS_SMS_ENABLED:
            try:
                message_id = await self.mts.sms_send(
                    phone,
                    settings.MTS_SMS_TEXT_TEMPLATE.format(
                        code=body.get('cert_code'),
                        charge_sum=body.get('charge_sum'),
                        balance=body.get('new_amount'),
                        status=body.get('status'),
                    ),
                )
                sent, error = await self.check_msg_with_retry(message_id)
            except NotCorrectPhoneNumberError:
                message_id, sent, error = (
                    None,
                    False,
                    'Not correct phone number',
                )

            if sent is True:
                logger.info(f'SMS to {phone} sent successfully.')
        else:
            message_id, sent, error = f'test_{uuid.uuid4()}', True, None
            logger.info(
                f'SMS sending is disabled. '
                f'Simulating successful send to {phone}.'
            )

        if message_id is not None or sent is not None or error is not None:
            tran_id = body.get('tran_id')
            await self.update_tran(tran_id, message_id, sent, error)


class RunUserEventsWorker(AsyncKafkaWorkerRunner):
    worker_class = SmsWorker


if __name__ == '__main__':
    RunUserEventsWorker().run()
