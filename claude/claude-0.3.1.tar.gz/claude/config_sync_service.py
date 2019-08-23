import json
import logging
from aiohttp.web import Request, WebSocketResponse
from aiohttp import WSMsgType
from time import time

from .config import default_dashboard_data, AppConfig
from .tools import dict_merge

logger = logging.getLogger(__name__)

clients = []

def find_removed_node(node: dict, data: dict):
    for key, value in node.items():
        if value is None:
            del data[key]
        else:
            find_removed_node(value, data[key])

class ConfigSyncService:

    def __init__(self, config: AppConfig):
        self._config = config

    async def controller(self, request: Request):

        ws = WebSocketResponse()

        await ws.prepare(request)

        clients.append(ws)

        logger.info("New client connected to the sync service")

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    message = json.loads(msg.data)

                    action = message['action']
                    diff = message['diff']

                    if not self._config.dashboard_config_loader.is_loaded:
                        self._config.dashboard_config_loader.data = default_dashboard_data

                    dict_merge(diff['added'], self._config.dashboard_config_loader.data)
                    dict_merge(diff['updated'], self._config.dashboard_config_loader.data)

                    find_removed_node(diff['deleted'], self._config.dashboard_config_loader.data)

                    # TODO: delay with some sec (and add if new trigger)
                    self._config.save()

                    dispatch_clients = list(filter(lambda c: c != ws, clients))

                    if dispatch_clients:

                        action['time'] = time()
                        action_msg = json.dumps(action)

                        logger.debug("Action dispatch to %s clients(s)", len(dispatch_clients))

                        for client in dispatch_clients:
                            await client.send_str(action_msg)

            elif msg.type == WSMsgType.ERROR:
                logger.error("ws connection closed with exception %s", ws.exception())

        logger.info("websocket connection closed")

        clients.remove(ws)

        return ws
