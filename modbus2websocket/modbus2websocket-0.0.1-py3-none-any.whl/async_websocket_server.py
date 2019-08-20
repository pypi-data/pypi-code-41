# -*- coding: utf-8 -*-

"""Async websocket server."""

import asyncio
import websockets
import json


class WebSocketError(Exception):
    """Web socket exceptions class."""

    pass


class AsyncWsClient(object):
    """Asyncio websocket client."""

    def __init__(self, *, queue=None, host='127.0.0.1', port=8888, timeout=1):
        """Init WS client. Using Queue in optional."""
        self.queue = queue
        self.host = host
        self.port = port
        self.timeout = timeout

    async def run_task(self):
        """Create and run task for loop."""
        task = websockets.serve(self._send, self.host, self.port)
        await task

    async def _send(self, websocket, path):
        """Send data as a websocket."""
        while True:
            try:
                if self.queue:
                    message = await self.queue.get()
                else:
                    message = {'message': 'test'}
                message = json.dumps(message)
                await websocket.send(message)
                await asyncio.sleep(self.timeout)
            except Exception as err:
                raise Exception(err)


if __name__ == '__main__':
    queue = asyncio.Queue()
    websocket_server = AsyncWsClient(
        host='127.0.0.1',
        port=8888,
        queue=queue,
    )
    asyncio.get_event_loop().run_until_complete(websocket_server.run_task())
    asyncio.get_event_loop().run_forever()
