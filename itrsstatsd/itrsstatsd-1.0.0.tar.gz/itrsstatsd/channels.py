# -*- coding: utf-8 -*-

import socket


class StdoutChannel:

    @staticmethod
    def send(message):
        print(message)


class RecordingChannel:

    def __init__(self):
        self.messages = []

    def send(self, message):
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
                self.channel.sendto(bytes(message, 'UTF-8'), (self.hostname, self.port))
            except OSError:
                print("Failed to send packet to {0}:{1}".format(self.hostname, self.port))




