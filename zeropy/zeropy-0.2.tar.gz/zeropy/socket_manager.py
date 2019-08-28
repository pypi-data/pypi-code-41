#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
from zeropy import proto, proto_manager


class SocketManager(object):
    host = '127.0.0.1'
    port = 38100

    sock_timeout = 10000
    manager = None
    connected = False
    proto = None
    response = None
    need_notify = False

    def __init__(self):
        self.manager = proto_manager.ProtoMananger()
        self.create_socket()

    def __del__(self):
        self.disconnect()

    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.sock_timeout is not None:
            self.sock.settimeout(self.sock_timeout)

    def connect(self, host=None, port=None):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        server_address = (self.host, self.port)
        try:
            self.sock.connect(server_address)
            self.connected = True
        except Exception as e:
            logging.error(str(e))

    def disconnect(self):
        if self.connected:
            self.sock.close()

    def is_connected(self):
        if self.connected:
            return True
        logging.error("no connection")
        return False

    def __send_data(self):
        send_status = False
        while send_status is False:
            try:
                self.sock.sendall(self.proto.buffer.raw)
                req_term = proto.TerminatingBlock()
                req_term.pack()
                self.sock.sendall(req_term.buffer.raw)
                send_status = True
            except socket.error as err:
                    print(err.errno)
                    self.connected = False
                    print("Attempting to connect...")
                    send_status = False

    def __recv(self, cmd, type, term_block):
        print('zeropy:socket_manager - try to recv cmd')
        recv_status = False
        while recv_status is False:
            try:
                self.response = proto.Header()
                if self.response.buf_size() is not 0:
                    self.sock.recv_into(self.response.buffer,
                                        self.response.buf_size())
                self.response.unpack()
                print('got responce cmd', self.response.cmd_num)

                data = None
                if type is proto.CMD_NUMS['GetBuffer'] or type is proto.CMD_NUMS['GetBufferPart']:
                    bytes_read = 0
                    buffer = bytearray(0)
                    while self.response.size > bytes_read:
                        buffer += self.sock.recv(8096)
                        bytes_read += 8096
                    if type is proto.CMD_NUMS['GetBuffer']:
                        import zeropy.utils as utils
                        if utils.check_crc32_sum(buffer) is not True:
                            print('Cannot check crc32 sum')
                            return
                    data = buffer
                else:
                    data = proto_manager.create_struct(type)
                    if data is None:
                        return
                    self.sock.recv_into(data.buffer,
                                            data.buf_size())
                    data.unpack()

                recv_status = True
                if term_block is True:
                    resp_block = proto.TerminatingBlock()
                    self.sock.recv_into(resp_block.buffer,
                                        resp_block.buf_size())
                    resp_block.unpack()

                return data
            except socket.error as err:
                    recv_status = False
                    print(err.errno)
                    self.connected = False
                    print("Attempting to connect...")


    def recv_into(self, _type):
        result = self.manager.recv_proto(_type)
        recv_status = False
        while recv_status is False:
            try:
                self.sock.recv_into(result.buffer,
                                    result.buf_size())
                result.unpack()
                recv_status = True
            except socket.error as err:
                print(err.errno)
                self.connected = False
                print("Attempting to connect...")
                self.reconnect()
                recv_status = False

        return result

    def method(self, *argc, _type, term_block):
        self.proto = proto_manager.create_proto(*argc, type=_type)
        #todo add log
        if self.proto is None:
            return None

        self.__send_data()
        cmd = self.manager.form_cmd(_type)
        result = self.__recv(cmd, _type, term_block)

        return result

