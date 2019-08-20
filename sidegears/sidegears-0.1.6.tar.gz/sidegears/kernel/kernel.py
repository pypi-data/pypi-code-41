"""Websocket rpc server that can be started and stopped by application.

Intended for use in browser-hosted applications. Backend software should
initialize RPCKernel and specify jsonrpcserver methods.

Uses jsonrpcserver (https://github.com/bcb/jsonrpcserver).

Handles request and notification messages from the client.
Also supports notification messages to the client, but
does *not* support sending request message from kernel to client.
"""

import asyncio
import json
import os
import sys

import websockets

import jsonrpcserver
rpc_method = jsonrpcserver.method

class RPCKernel:
    """Encapsulates websocket/jsonrpc server code.

    """
    def __init__(self):
        # async queue for (output) notification messages
        self._output_queue = asyncio.Queue(maxsize=10)

        # Flag used as part of logic to stop websocket server
        self._running = False

        # websocket server
        self._server = None

        # jsonrpcserver configuration options
        self._config = dict(basic_logging=False, debug=False, trim_log_values=False)

        # option to close the server when client disconnects
        self._close_on_disconnect = False

    def start(self, host='localhost', port='5678', close_on_disconnect=False):
        """Instantiates and starts websocket server

        """
        if self._running:
            raise Exception('Server already running')

        self._close_on_disconnect = close_on_disconnect
        self._running = True
        start_server = websockets.serve(self._handler, host, port)
        loop = asyncio.get_event_loop()
        self._server = loop.run_until_complete(start_server)
        print('Started ws server at %s:%s' % (host, port))

    def stop(self):
        """Stops the handler, and waits for server to finish

        Stumbled into how to do this at:
        https://github.com/aaugustin/websockets/issues/39
        (websockets docs no help)
        """
        self._running = False
        self._server.close()
        loop = asyncio.get_event_loop()
        #loop.run_until_complete(self._server.wait_closed())
        return self._server.wait_closed()

    def wait_until_closed(self):
        """Block until server closes.

        Should be used when the on_close_disconnect flag is set.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._server.wait_closed())

    def send_notification(self, method, params=None):
        """Formats and enqueues outbound jsonrpc notification (request)

        (Output queue is polled in the _producer method)
        """
        print('Sending notification, method {}'.format(method))
        notify_object = dict()
        notify_object['jsonrpc'] = '2.0'
        notify_object['method'] = method
        if params:
            notify_object['params'] = params
        notify_string = json.dumps(notify_object)
        self._output_queue.put_nowait(notify_string)

    def set_basic_logging(self, enabled):
        self._config['basic_logging'] = bool(enabled)

    def set_debug(self, enabled):
        self._config['debug'] = bool(enabled)

    def set_trim_log_values(self, enabled):
        self._config['trim_log_value'] = bool(enabled)

    async def _producer(self):
        """Async method to poll output queue for messages

        """
        while self._running:
            if self._output_queue.empty():
                await asyncio.sleep(1)
            else:
                item = self._output_queue.get_nowait()
                return item
        return 'test output'

    async def _handler(self, websocket, path):
        """Async method to handles websocket connections

        """
        producer_task = None  # in case self._running is False
        while self._running:
            listener_task = asyncio.ensure_future(websocket.recv())
            producer_task = asyncio.ensure_future(self._producer())
            done, pending = await asyncio.wait(
                [listener_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED)
            #print('done', done)
            #print('pending', pending)

            if listener_task in done:
                try:
                    request = listener_task.result()
                except websockets.exceptions.ConnectionClosed as ex:
                    # print('websockets.exceptions.ConnectionClosed:', ex)
                    if self._close_on_disconnect:
                        print('Connection closed:', ex.code)
                        self._running = False
                        self._server.close()
                except Exception as ex:
                    self._running = False
                    print('EXCEPTION:', ex)
                else:
                    #print('request', request)
                    response = await jsonrpcserver.async_dispatch(request, **self._config)
                    if response:
                        await websocket.send(str(response))
            else:
                listener_task.cancel()

            if producer_task in done:
                message = producer_task.result()
                if self._config['basic_logging']:
                    print('<<<', message)
                await websocket.send(message)
            else:
                producer_task.cancel()

        # When loop exits, wait for last producer task
        if (producer_task):
            await asyncio.wait([producer_task])

        # Close the socket
        websocket.close()


if __name__ == '__main__':
    # This code only works for ONE websocket connect.
    # Doesn't support closing and restarting new connection.

    import platform
    if platform.system() == 'Windows':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    @rpc.method
    async def quit():
        """Stop the websocket server.

        This should called as a notification message, so that no response
        is required.
        """
        print('Received quit message')
        server.stop()
        return True

    @rpc.method
    async def logToKernel(request):
        print('Received logToKernel request with text:', request)
        return {'status': 'logged'}

    import functools
    @rpc.method
    async def echo(text, delay=None):
        print('Received echo request')
        if not delay:
            return {'status': 'no echo specified'}

        if isinstance(delay, str):
            delay = float(delay)
        loop = asyncio.get_event_loop()
        loop.call_later(
            delay, functools.partial(server.send_notification, 'echo', text))
        return {'status': 'will do'}

    print('rpc.methods', rpc.methods.Methods)
    print(dir(rpc.methods.Methods))

    server = RPCKernel()
    server.set_basic_logging(True)
    server.set_debug(True)
    server.set_trim_log_values(False)
    server.start()

    loop = asyncio.get_event_loop()
    # Use this hack to exit when the websocket server is closed
    loop.run_until_complete(server._server.wait_closed())
