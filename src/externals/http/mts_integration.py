import logging
from typing import Optional
from logging import config as logging_config

import requests
import time
from aiohttp import BasicAuth as HTTPBasicAuth

from dotenv import load_dotenv

import settings
from externals.http.base import BaseApiClient, BaseApiClientResponse

load_dotenv()

logging_config.dictConfig(settings.LOGGING)
logger = logging.getLogger('wizard')


class NotCorrectPhoneNuberError(Exception):
    pass


class MtsAPI(BaseApiClient):
    sleep_time = 60

    @property
    def base_url(self) -> str:
        return settings.MTS_BASE_URL

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
            text_message: str
    ) -> BaseApiClientResponse:
        url = settings.MTS_SEND_MSG_URL
        body = {
            "messages": [
                {
                    "content": {
                        "short_text": text_message
                    },
                    "from": {
                        "sms_address": naming
                    },
                    "to": [
                        {
                            "msisdn": to
                        }
                    ]
                }]
        }
        return await self.post(
            url, json=body, auth=HTTPBasicAuth(login, password)
        )


    def check_balance(self, login: str, password: str) -> int:
        url = 'https://omnichannel.mts.ru/http-api/v1/messages/balanceManagement/balance/full'
        resp_info = requests.post(url, auth=HTTPBasicAuth(login, password))
        if resp_info.status_code == 200:
            try:
                balance = float(resp_info.json()["balance"])
            except (KeyError, AttributeError, TypeError):
                balance = 0
        else:
            balance = 0
        return balance

    def check_message(
            self, login: str, password: str, message_id: str
    ) -> (Optional[bool], Optional[str]):
        url = settings.MTS_CHECK_MSG_URL
        body = {"int_ids": [message_id]}
        try:
            response = self.post(url, data=body, auth=HTTPBasicAuth(login, password))
            event_code = response["events_info"][0]["events_info"][0]["status"]
            if event_code == 200:
                return True, None
            elif event_code == 201:
                error_reason = response["events_info"][0]["events_info"][0]['internal_errors']
                return False, error_reason
        except Exception:
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
            sms_text
        )

        print('RESPONSE SMS SEND', response)
        message_id = response.parsed_response['messages'][0]["internal_id"]
        return message_id

    def sms_report(self, final_user_list: list, start_balance: int) -> dict:
        """Формирует отчет об отправленных смс."""
        time.sleep(self.sleep_time)
        unsuccess_sms = 0
        for user in final_user_list:
            phone = user['phone']
            if phone != 'НЕ УКАЗАН':
                sms_id = user['sms_id']
                sms_status, error_reason = self.check_message(settings.MTS_LOGIN, settings.MTS_PASSWORD, sms_id)
                if sms_status:
                    user['status'] = 'ДОСТАВЛЕНО'
                elif sms_status is None:
                    user['status'] = 'НЕ ИЗВЕСТНО'
                else:
                    unsuccess_sms += 1
                    user['status'] = 'НЕ ДОСТАВЛЕНО'
                    user['error_reason'] = error_reason
        final_balance = self.check_balance(settings.MTS_LOGIN, settings.MTS_PASSWORD)
        return {
            'Clients': len(final_user_list),
            'Unsuccess': unsuccess_sms,
            'Costs': int(start_balance) - int(final_balance),
            'Balance': final_balance
        }