import asyncio
import json
import logging
import os
import sys
from logging import config as logging_config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings
from core.workers import AsyncKafkaBaseWorker, AsyncKafkaWorkerRunner
from externals.http.telegram_integration import TelegramAPI

logging_config.dictConfig(settings.LOGGING)
logger = logging.getLogger(settings.PROJECT)


class TelegramWorker(AsyncKafkaBaseWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_client = TelegramAPI()

    @staticmethod
    def get_topics():
        return [settings.KAFKA_TELEGRAM_TOPIC]

    async def handle(self, message):
        body = json.loads(message.value.decode('utf-8'))
        chat_id = body.get('chat_id')
        image_url = body.get('image_url')
        text = body.get('text')

        res = await self.telegram_client.send_certificate(
            chat_id, image_url, text
        )
        if res.status != 200:
            logger.error(
                'Failed to send certificate for chat_id: %s, error: %s',
                chat_id,
                res.parsed_response,
            )
        else:
            logger.info(
                'Telegram message successfully sent to chat_id %s', chat_id
            )


class RunUserEventsWorker(AsyncKafkaWorkerRunner):
    worker_class = TelegramWorker


if __name__ == '__main__':
    RunUserEventsWorker().run()
