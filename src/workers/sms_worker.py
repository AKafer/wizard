import logging
import os
import sys
from logging import config as logging_config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings
from core.workers import AsyncKafkaBaseWorker, AsyncKafkaWorkerRunner

logging_config.dictConfig(settings.LOGGING)
logger = logging.getLogger('wizard')


class SmsWorker(AsyncKafkaBaseWorker):
    @staticmethod
    def get_topics():
        return [settings.KAFKA_SMS_TOPIC]

    async def handle(self, message):
        print('topic:', message.topic)
        print('key:', message.key)
        print('value(raw):', message.value)
        logger.info('MESSAGE: %s', message.value)


class RunUserEventsWorker(AsyncKafkaWorkerRunner):
    worker_class = SmsWorker


if __name__ == '__main__':
    RunUserEventsWorker().run()
