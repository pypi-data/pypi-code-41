from enum import Enum
from typing import Union, Optional, TypeVar, List, Any

import aiohttp
from pygramtic.models import InlineKeyboardMarkup, ReplyKeyboardRemove, ForceReply, \
    ReplyKeyboardMarkup, Message, InputFile

ReplyMarkupTypes = TypeVar('ReplyMarkupTypes', InlineKeyboardMarkup, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, ForceReply)


class APIMethod(str, Enum):
    setWebhook = 'setWebhook'

    sendMessage = 'sendMessage'


class Bot:
    def __init__(self, token: str):
        self.token = token

    async def request(self, method: APIMethod, data: dict) -> Any:
        url = f'https://api.telegram.org/bot{self.token}/{method.value}'
        print(url)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if not response.status == 200:
                    print(response.reason)
                    raise Exception('Request failed', response.content)
                as_json = await response.json()
                if not as_json['ok']:
                    raise Exception('Response is not ok:', as_json)
                return as_json['result']

    async def send_message(
            self, chat_id: Union[int, str], text: str,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: Optional[bool] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[ReplyMarkupTypes] = None) -> Message:

        payload = {
            'chat_id': chat_id,
            'text': text,
        }

        if parse_mode:
            payload['parse_mode'] = parse_mode
        if disable_web_page_preview:
            payload['disable_web_page_preview'] = disable_web_page_preview
        if disable_notification:
            payload['disable_notification'] = disable_notification
        if reply_to_message_id:
            payload['reply_to_message_id'] = reply_to_message_id
        if reply_markup:
            payload['reply_markup'] = reply_markup.json(skip_defaults=True)

        result = await self.request(APIMethod.sendMessage, payload)

        return Message(**result)

    async def set_webhook(
            self,
            url: str,
            certificate: Optional[InputFile] = None,
            max_connections: int = None,
            allowed_updates: List[str] = None) -> bool:

        payload = {
            'url': url
        }

        if certificate:
            payload['certificate'] = certificate
        if max_connections:
            payload['max_connections'] = max_connections
        if allowed_updates:
            payload['allowed_updates'] = allowed_updates

        result = await self.request(APIMethod.setWebhook, payload)

        if not isinstance(result, bool):
            raise Exception('Received response is not boolean: ', result)

        return result
