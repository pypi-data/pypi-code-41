#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate asyncio connections by wrapping them into a Connection"""

import asyncio
import logging
import pickle
from collections import namedtuple
from typing import Optional

from ujotypes import UjoMap, read_buffer, ujo_to_python, UjoStringC

import titanfe.log
from titanfe.simplified_ujo import py_to_ujo_bytes

ENCODING = "UJO"
# ENCODING = "PICKLE"

PAYLOAD = UjoStringC("payload")

NetworkAddress = namedtuple("NetworkAddress", ("host", "port"))


def decode_ujo_but_keep_payload(ujo_bytes):
    """Decode ujo bytes into a corresponding python object, but keep an existing "Payload" as Ujo.
    """
    ujoobj = read_buffer(ujo_bytes)

    payload = None
    if isinstance(ujoobj, UjoMap) and PAYLOAD in ujoobj:
        payload = ujoobj[PAYLOAD]
        del ujoobj[PAYLOAD]

    pyobj = ujo_to_python(ujoobj)

    if payload is not None:
        # set payload to the original ujo payload
        pyobj["payload"] = payload

    return pyobj


class Connection:
    """Wrap an asyncio StreamReader/Writer combination into a connection object.

     Arguments:
         reader (asyncio.StreamReader): the stream reader
         writer (asyncio.StreamWriter): the stream writer
         log (logging.logger): a parent logger
         encoding: "PICKLE" or "UJO"
     """

    def __init__(self, reader, writer, log=None, encoding=ENCODING):
        self.reader = reader
        self.writer = writer

        self.log = log.getChild("Connection") if log else titanfe.log.getLogger(__name__)

        if encoding == "PICKLE":
            self.decode = pickle.loads
            self.encode = pickle.dumps
        elif encoding == "UJO":
            self.decode = decode_ujo_but_keep_payload
            self.encode = py_to_ujo_bytes

    @classmethod
    async def open(
            cls, address: NetworkAddress, log: Optional[logging.Logger] = None
    ) -> "Connection":
        """open an asyncio connection to the given address (host, port)"""
        reader, writer = await asyncio.open_connection(*address)
        return cls(reader, writer, log)

    async def receive(self):
        """wait until a message comes through and return it's content after decoding"""
        msg_len = await self.reader.readexactly(4)
        msg = await self.reader.readexactly(int.from_bytes(msg_len, "big"))

        self.log.debug("received message: %s", msg)
        try:
            content = self.decode(msg)
        except Exception:
            self.log.error("Failed to decode %r", msg, exc_info=True)
            raise ValueError(f"Failed to decode {msg}")

        self.log.debug("decoded message: %r", content)
        return content

    async def send(self, content):
        """encode and send the content as a message"""
        self.log.debug("sending: %r", content)
        try:
            msg = self.encode(content)
        except Exception:
            self.log.error("Failed to encode %r", content, exc_info=True)
            raise ValueError(f"Failed to encode {content}")

        msg_len = len(msg).to_bytes(4, "big")
        self.writer.write(msg_len)
        self.writer.write(msg)
        await self.writer.drain()
