import asyncio
import websockets


async def hello():
    uri = "ws://localhost:6543"
    async with websockets.connect(uri) as websocket:
        msg = await websocket.recv()
        print(msg)

asyncio.get_event_loop().run_until_complete(hello())
