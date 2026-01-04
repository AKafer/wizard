import json
import logging
import os
import sys
from logging import config as logging_config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings
from externals.http.mts_integration import MtsAPI
from core.workers import AsyncKafkaBaseWorker, AsyncKafkaWorkerRunner

logging_config.dictConfig(settings.LOGGING)
logger = logging.getLogger('wizard')


class SmsWorker(AsyncKafkaBaseWorker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mts = MtsAPI()

    @staticmethod
    def get_topics():
        return [settings.KAFKA_SMS_TOPIC]

    async def handle(self, message):
        logger.info('MESSAGE: %s', message.value)
        body = json.loads(message.value.decode('utf-8'))

        phone = body.get('phone')
        print('body', body)
        print('phone:', phone)

        message_id = await self.mts.sms_send(phone, 'Test message from wizard service')
        print('message_id:', message_id)




class RunUserEventsWorker(AsyncKafkaWorkerRunner):
    worker_class = SmsWorker


if __name__ == '__main__':
    RunUserEventsWorker().run()
