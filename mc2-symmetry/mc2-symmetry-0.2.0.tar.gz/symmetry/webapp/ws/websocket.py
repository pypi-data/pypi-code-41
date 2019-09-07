import asyncio
import json
from multiprocessing import Process

import websockets
from aioredis import create_connection, Channel


class TelemetryWebsocket:
    def __init__(self, redis_address):
        self.redis_address = redis_address

    async def subscribe_to_redis(self, path):
        conn = await create_connection((self.redis_address[0], self.redis_address[1]))
        # Set up a subscribe channel
        channel = Channel(path, is_pattern=True)
        await conn.execute_pubsub('psubscribe', channel)
        return channel, conn

    async def handler(self, websocket, path):
        channel, conn = await self.subscribe_to_redis(path[1:])
        try:
            while True:
                # Wait until data is published to this channel
                messages = await channel.get()
                # Send unicode decoded data over to the websocket client
                if len(messages) == 2:
                    data = {
                        "topic": messages[0].decode('utf-8'),
                        "value": messages[1].decode('utf-8')
                    }
                    await websocket.send(json.dumps(data))

        except websockets.exceptions.ConnectionClosed:
            # Free up channel if websocket goes down
            await conn.execute_pubsub('punsubscribe', channel)
            conn.close()
        finally:
            conn.close()


class WebsocketServer:

    def __init__(self, ws_address=("0.0.0.0", 8082), redis_address=("localhost", 6379)):
        super().__init__()
        self.ws_address = ws_address
        self.redis_address = redis_address
        self.loop = None
        self.server = None

    def start(self):
        p = Process(target=self.run, name='Websocket Service')
        p.start()

    def run(self):
        try:
            self.loop = asyncio.get_event_loop()
            telemetry_websocket = TelemetryWebsocket(self.redis_address)
            start_server = websockets.serve(telemetry_websocket.handler, self.ws_address[0], self.ws_address[1])
            self.server = self.loop.run_until_complete(start_server)
            self.loop.run_forever()
        finally:
            self.close()

    def stop(self):
        if self.loop is not None:
            self.loop.stop()

    def close(self):
        if self.server is not None:
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.server = None

        if self.loop is not None:
            self.loop.close()
            self.loop = None
