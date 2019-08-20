import json
import logging
import os
import pytz
import requests
import socket

from logging.handlers import HTTPHandler
from datetime import datetime

logger = logging.getLogger(__name__)


class LokiHandler(HTTPHandler):

    def __init__(self, host, url):
        """
        The host string has to contain the protocol
        prefix (http or https) with port and url is
        just the path
        """
        self._break_post = False
        super().__init__(host, url, 'POST')

    def break_post(self, boolean):
        self._break_post = boolean

    def _get_host(self):
        """
        Get DNS name of the host
        """

        return socket.gethostname()

    def _get_service_name(self):
        """
        Get the service name using SERVICE_NAME
        env enviroment variable
        """

        return os.getenv('SERVICE_NAME') or 'UNKONW'

    def format(self, record):
        """Formata a mensagem como um json e envia para o emit()"""

        payload = {
            'streams': [
                {
                    'labels': '{filename="%s",service="%s", host="%s"}' % (
                        record.filename,
                        self._get_service_name(),
                        self._get_host()
                    ),
                    'entries': [
                        {
                            'ts': datetime.now(
                                pytz.timezone(  # TODO change timezone
                                    'Asia/Yekaterinburg')
                            ).isoformat('T'),
                            'line': f"[{record.levelname}] {str(datetime.now())[:10]}|\
                            {record.filename}-{record.funcName}-{record.lineno}:\
                            {record.msg}",
                        }
                    ]
                }
            ]
        }

        return json.dumps(payload)

    def emit(self, record):
        """Enviar uma requisição para o serviço Loki"""

        payload = self.format(record)

        url_host = os.path.join(
            self.host,
            self.url
        )

        try:
            requests.post(
                url_host,
                data=payload,
                headers={'Content-type': 'application/json'}
            )
        except Exception:
            if self._break_post:
                raise Exception("Don't have connection with Loki")
            else:
                logger.debug("Handler can not send the message to Loki")
