import logging
from logging import config as logging_config

import settings
from externals.http.base import BaseApiClient

logging_config.dictConfig(settings.LOGGING)
logger = logging.getLogger(settings.PROJECT)


class TelegramAPI(BaseApiClient):

    @property
    def base_url(self) -> str:
        return settings.TELEGRAM_API_BASE_URL

    def get_send_foro_url(self):
        return f'/bot{settings.TELEGRAM_TOKEN}/sendPhoto'

    async def send_certificate(self, chat_id: int, image_url: str, text: str):
        payload = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": text,
            "parse_mode": "HTML"
        }

        return await self.post(
            endpoint=self.get_send_foro_url(),
            json=payload,
            raise_for_status=False
        )
