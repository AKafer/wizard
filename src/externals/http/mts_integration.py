import logging
from logging import config as logging_config
from typing import Any, Optional

import requests
from aiohttp import BasicAuth as HTTPBasicAuth

import settings
from externals.http.base import BaseApiClient, BaseApiClientResponse

logging_config.dictConfig(settings.LOGGING)
logger = logging.getLogger('wizard')


NOT_FOUND_MSG_ERROR = 'Message ID not found'


class NotCorrectPhoneNuberError(Exception):
    pass


class MtsAPI(BaseApiClient):
    sleep_time = 60

    @property
    def base_url(self) -> str:
        return settings.MTS_BASE_URL

    def deep_get(self, obj: Any, path: list[Any], default=None):
        if obj is None:
            return default
        cur = obj
        for key in path:
            try:
                cur = cur[key]
            except (TypeError, KeyError, IndexError):
                return default
        return cur

    def correc_number(self, phone: str) -> str:
        """Format to 7-XXX-XXX-XXXX"""
        if phone.startswith('+7'):
            phone = phone[1:]
        elif phone.startswith('8'):
            phone = f'7{phone[1:]}'
        elif phone.startswith('7'):
            pass
        else:
            raise NotCorrectPhoneNuberError
        return phone

    async def sent_message(
        self,
        login: str,
        password: str,
        naming: str,
        to: str,
        text_message: str,
    ) -> BaseApiClientResponse:
        url = settings.MTS_SEND_MSG_URL
        body = {
            'messages': [
                {
                    'content': {'short_text': text_message},
                    'from': {'sms_address': naming},
                    'to': [{'msisdn': to}],
                }
            ]
        }
        return await self.post(
            url, json=body, auth=HTTPBasicAuth(login, password)
        )

    def check_balance(self, login: str, password: str) -> int:
        url = settings.MTS_CHECK_BALANCE_URL
        resp_info = requests.post(url, auth=HTTPBasicAuth(login, password))
        if resp_info.status_code == 200:
            try:
                balance = float(resp_info.json()['balance'])
            except (KeyError, AttributeError, TypeError):
                balance = 0
        else:
            balance = 0
        return balance

    async def check_message(
        self, message_id: str
    ) -> (Optional[bool], Optional[str]):
        url = settings.MTS_CHECK_MSG_URL
        body = {'int_ids': [message_id]}
        try:
            response = await self.post(
                url,
                json=body,
                auth=HTTPBasicAuth(settings.MTS_LOGIN, settings.MTS_PASSWORD),
                raise_for_status=False
            )
            logger.info('DEBUG-1: MTS response: %s', response)
            if response.status == 404:
                return None, NOT_FOUND_MSG_ERROR

            logger.info('DEBUG=2: MTS parsed response: %s', response.parsed_response)
            event_code = self.deep_get(
                response.parsed_response,
                ['events_info', 0, 'events_info', 0, 'status'],
            )
            logger.info('DEBUG-3: MTS event code: %s', event_code)
            if event_code == 200:
                return True, None
            elif event_code == 201:
                error_reason = self.deep_get(
                    response.parsed_response,
                    ['events_info', 0, 'events_info', 0, 'internal_errors'],
                )
                return False, error_reason
            else:
                logger.warning(
                    'Unknown event code %s for message id %s',
                    event_code,
                    message_id,
                )
                return None, None
        except Exception:
            logger.exception("Error checking message status for id %s", message_id)
            return None, None

    async def sms_send(self, raw_phone: str, sms_text: str) -> str:
        try:
            phone = self.correc_number(raw_phone)
        except NotCorrectPhoneNuberError:
            logger.error(f'Phone number {raw_phone} not recognized')
            raise NotCorrectPhoneNuberError

        response = await self.sent_message(
            settings.MTS_LOGIN,
            settings.MTS_PASSWORD,
            settings.MTS_NAME,
            phone,
            sms_text,
        )

        message_id = self.deep_get(
            response.parsed_response, ['messages', 0, 'internal_id']
        )
        if message_id is None:
            logger.error(
                f'Failed to send SMS to {phone}, response: {response}'
            )
        return message_id
