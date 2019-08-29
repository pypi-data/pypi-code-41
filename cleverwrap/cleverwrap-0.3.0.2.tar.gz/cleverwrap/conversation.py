import requests

from cleverwrap.errors import UnknownAPIError
from cleverwrap.response import Response

__all__ = ('Conversation',)


class Conversation:
    def __init__(self, api):
        self.api = api
        self.cs = ""
        self.convo_id = ""

    def say(self, text):
        """
        Say something to www.cleverbot.com

        :type text: string
        :rtype: string
        """

        params = {
            "input": text,
            "cs": self.cs,
            "conversation_id": self.convo_id,
        }

        try:
            data = self.api._send(params, raise_for_status=True)
        except requests.RequestException as e:
            raise UnknownAPIError() from e

        reply = Response(data)
        self.cs = reply.cs
        self.convo_id = reply.convo_id
        return reply.output

    def reset(self):
        """
        Drop values for self.cs and self.conversation_id
        this will start a new conversation with the bot.
        """
        self.cs = ""
        self.convo_id = ""
