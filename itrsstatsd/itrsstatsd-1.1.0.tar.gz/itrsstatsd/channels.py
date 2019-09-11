# -*- coding: utf-8 -*-

import os
import socket
import sys
import time

class StdoutChannel:

    @staticmethod
    def send(message):
        print(message)

    def close(self):
        pass


class RecordingChannel:

    def __init__(self, slow=False):
        self.messages = []
        self.slow = slow

    def close(self):
        pass

    def send(self, message):
        if self.slow:
            time.sleep(5)
        self.messages.append(message)

    def get_messages(self):
        return self.messages


class UdpChannel:

    def __init__(self, hostname, port):
        self.port = port
        self.hostname = hostname
        self.channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self):
        self.channel.close()
        self.channel = None

    def send(self, message):
        if self.channel is not None:
            try:
                self.channel.sendto(bytes(message + '\n', 'UTF-8'), (self.hostname, self.port))
            except OSError as e:
                print("Failed to send statsd message to {0}:{1} - {2}".format(
                    self.hostname, self.port, os.strerror(e.errno)), file=sys.stderr)


class TcpChannel:

    def __init__(self, hostname, port):
        self.port = port
        self.hostname = hostname
        self.last_connect_attempt = 0
        self.channel = None
        self._connect()

    def _connect(self):
        now = int(time.time())
        if now - self.last_connect_attempt > 10:
            self.last_connect_attempt = now
            try:
                self.channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.channel.connect((self.hostname, self.port))
                return True
            except OSError as e:
                print("Failed to connect to statsd server: {0}".format(os.strerror(e.errno)), file=sys.stderr)
                self.close()
        return False

    def close(self):
        self.channel.close()
        self.channel = None

    def send(self, message):
        if self.channel is None and not self._connect():
            return

        try:
            self.channel.send(bytes(message + '\n', 'UTF-8'))
        except OSError as e:
            print("Failed to send statsd message to {0}:{1} - {2}".format(
                self.hostname, self.port, os.strerror(e.errno)), file=sys.stderr)
            self.close()
