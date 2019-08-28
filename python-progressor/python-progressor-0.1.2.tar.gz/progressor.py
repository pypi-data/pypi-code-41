#!/usr/bin/env python3
# coding: utf-8
import time
import socket
import json
import contextlib
import sys

from collections import Sized, Iterable
from jsonrpc_requests import Server as BaseRPCClient


DEFAULT_TTL = 10 * 60
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 7890


class Response():
    def __init__(self, body):
        self.body = body

    def json(self):
        decoded = self.body.decode('utf-8')
        return json.loads(decoded)


class CommunicationError(RuntimeError):
    pass

class UnableToSendRequest(CommunicationError):
    pass

class UnableToReadResponse(CommunicationError):
    pass


class RPCClient(BaseRPCClient):
    def __init__(self, host='localhost', port=7890):
        # self.socket.setblocking(False)
        self.host = host
        self.port = port
        self.next_command_id = 0
        self.socket = None

    def __enter__(self):
        self.reconnect()
        return self

    def __exit__(self, *args, **kwargs):
        self.socket.close()
        self.socket = None

    def reconnect(self):
        if self.socket:
            self.socket.close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect_ex((self.host, self.port))
        except:
            self.socket = None

    def send_request(self, method_name, is_notification, params):
        # content = self.serialize(method_name, params, is_notification).encode('utf-8')
        # content_length = len(content)
        # header = 'Content-Length: {}\r\n\r\n'.format(content_length).encode('utf-8')
        content = self.serialize(method_name, params, is_notification)
        content_length = len(content)
        header = 'Content-Length: {}\r\n\r\n'.format(content_length)
        request = header + content

        try:
            self.socket.sendall(request.encode('utf-8'))
        except socket.error:
            raise UnableToSendRequest()

        if not is_notification:
            response = self.read_response()
            return self.parse_response(response)

    def read_response(self):
        approximate_header_size = len('Content-Length:') * 4
        delimiter = '\r\n\r\n'

        header = self.socket.recv(approximate_header_size)
        if not header:
            raise UnableToReadResponse('No data was received')

        if delimiter not in header:
            raise UnableToReadResponse('No Content-Length header')

        headers, body = header.split(delimiter)

        def parse_header(line):
            name, value = line.split(':', 1)
            return (
                name.strip().lower(),
                value.strip().lower(),
            )

        headers = dict(map(parse_header, headers.split('\n')))

        if 'content-length' not in headers:
            raise UnableToReadResponse('No Content-Length header')

        try:
            content_length = int(headers['content-length'])
        except ValueError:
            raise UnableToReadResponse('Bad value in Content-Length header')

        block_size = 1024
        remaining_length = content_length - len(body)

        while remaining_length > 0:
            received = self.socket.recv(min(block_size, remaining_length))
            if not received:
                raise UnableToReadResponse('Error during fetching response body')

            body += received
            remaining_length = content_length - len(body)

        return Response(body)


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
        self.pending_increments = 0

    def increment(self, value=1):
        self.pending_increments += value

        try:
            self.client.increment(
                id=self.id,
                value=self.pending_increments,
            )
            self.pending_increments = 0
        except CommunicationError:
            self.client.reconnect()
                 

@contextlib.contextmanager
def create_progress(id=None,
                    description=None,
                    total=None,
                    current=0,
                    ttl=DEFAULT_TTL,
                    host=DEFAULT_HOST,
                    port=DEFAULT_PORT):
    with RPCClient() as client:
        if id is None:
            id = str(int(time.time()))

        response = client.create(
            id=id,
            description=description,
            total=total,
            current=current,
            ttl=ttl,
        )
        yield Progress(client, **response)


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

    with create_progress(
            host=host,
            port=port,
            total=total,
            description=description,
            ttl=ttl,
        ) as progress:
        for item in obj:
            yield item
            progress.increment()


if __name__ == '__main__':
    to_number = 100
    description = 'From 1 to {}'.format(to_number)

    if len(sys.argv) > 1:
        description = sys.argv[1]

    if len(sys.argv) > 2:
        to_number = int(sys.argv[2])

    for i in p(range(to_number),
               description=description,
               ttl=3600):
        time.sleep(0.1)
        print(i)
