# -*- coding: utf-8 -*-
"""Opens a websocket and returns messages"""

import json
import time

import click
import websocket

from quare.quip import QuipClient
from quare.quip_classes import QuipMessage

HEARTBEAT_INTERVAL = 20


def stream_updates(token):
    def on_message(ws, message):
        message = json.loads(message)
        if message.get("type") == "message":
            thread = message["thread"]["title"]
            try:
                msg = QuipMessage.from_dict(message.get("message"))
                msg.print(msg, thread=thread)
            except Exception as e:
                print(e)
                ws.close()

    def on_error(ws, error):
        pass

    def on_close(ws):
        click.secho("\n")
        click.secho("...connection closed.", bold=True)

    def on_open(ws):
        click.secho("Streaming updates... press Ctrl-C to exit.", bold=True)

        def run(*args):
            while True:
                time.sleep(HEARTBEAT_INTERVAL)
                ws.send(json.dumps({"type": "heartbeat"}))

    client = QuipClient(token)
    url = client.new_websocket().get("url")
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        url, on_message=on_message, on_error=on_error, on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()
