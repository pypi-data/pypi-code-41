#/usr/bin/env python3

import time
import socket
import json

from typing import Sized, Iterable
from jsonrpc_requests import Server as BaseRPCClient


DEFAULT_TTL = 10 * 60
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 7890


class Response():
    def __init__(self, body):
        self.body = body

    def json(self):
        decoded = self.body.decode('utf-8')
        headers, body = decoded.split('\r\n\r\n')
        return json.loads(body)


class RPCClient(BaseRPCClient):
    def __init__(self, host='localhost', port=7890):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.connected = False
        self.next_command_id = 0

    def __enter__(self):
        self.socket.connect((self.host, self.port))
        self.connected = True
        return self

    def __exit__(self, *args, **kwargs):
        self.socket.close()
        self.connected = False

    def send_request(self, method_name, is_notification, params):
        # content = self.serialize(method_name, params, is_notification).encode('utf-8')
        # content_length = len(content)
        # header = 'Content-Length: {}\r\n\r\n'.format(content_length).encode('utf-8')
        content = self.serialize(method_name, params, is_notification)
        content_length = len(content)
        header = 'Content-Length: {}\r\n\r\n'.format(content_length)
        request = header + content
        self.socket.sendall(request.encode('utf-8'))

        if not is_notification:
            response = self.socket.recv(1024 * 4)
            return self.parse_response(Response(response))


class Progress():
    def __init__(self,
                 rpc_client,
                 id=None,
                 description=None,
                 total=None,
                 current=None):
        self.client = rpc_client
        self.id = id
        self.description = description
        self.total = total
        self.current = current

    def increment(self, value=1):
        self.client.increment(
            id=self.id,
            value=value,
        )
                 

def create_progress(client, id=None, description=None, total=None, current=0, ttl=DEFAULT_TTL):
    if id is None:
        id = str(int(time.time()))
        response = client.create(
            id=id,
            description=description,
            total=total,
            current=current,
            ttl=ttl,
        )
        return Progress(client, **response)


def p(obj,
      total=None,
      description=None,
      ttl=DEFAULT_TTL,
      host=DEFAULT_HOST,
      port=DEFAULT_PORT):
    if not isinstance(obj, Iterable):
        raise RuntimeError('Progress could be tracked only for iterable objects')
    
    if total is None and isinstance(obj, Sized):
        total = len(obj)

    with RPCClient() as client:
        progress = create_progress(
            client,
            total=total,
            description=description,
            ttl=ttl,
        )
        for item in obj:
            yield item
            progress.increment()


if __name__ == '__main__':
    for i in p(range(100),
               description='От 1 до 100',
               ttl=3600):
        time.sleep(0.1)
        print(i)
