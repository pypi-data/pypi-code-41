# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Multiple Modbus Server using asyncio."""

import asyncio
from random import SystemRandom
from pyModbusTCP.server import ModbusServer, DataBank
import concurrent


class ServerError(Exception):
    """Server Exception class."""

    pass


class AsyncModbusServer(object):
    """Asynchronous Modbus TCP Server."""

    def __init__(
        self,
        *,
        host='127.0.0.1',
        bit_adr=0,
        bit_num=1,
        word_adr=0,
        word_num=1,
        timeout=1,
        name='Modbus Server',
    ):
        """Init server."""
        self.port = 502
        self.host = host
        self.bit_adr = bit_adr
        self.bit_num = bit_num
        self.word_adr = word_adr
        self.word_num = word_num
        self.timeout = timeout
        self.name = name
        self.connection = None
        try:
            self.connection = ModbusServer(
                host=self.host,
                port=self.port,
                no_block=True,
            )
            self.connection.start()
        except Exception as err:
            raise ServerError('Error with server', err)

    async def run_task(self):
        """Run asyncio server."""
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=3,
        )
        task = asyncio.create_task(self._awaitable(executor))
        await task

    def stop(self):
        """Stop server."""
        self.connection.stop()

    def start_task(self):
        """Create async task."""
        return asyncio.create_task(self._setup())

    def _setup(self):
        cryptogen = SystemRandom()
        while True:
            bits_value = [
                bool(cryptogen.randrange(2)) for
                indx in range(self.bit_num)
            ]
            words_value = [
                cryptogen.randrange(10) for
                _ in range(self.word_num)
            ]
            try:
                DataBank.set_bits(self.bit_adr, bits_value)
                DataBank.set_words(self.word_adr, words_value)
            except Exception as err:
                raise ServerError('Error with writing', err)

    async def _awaitable(self, executor):
        loop = asyncio.get_event_loop()
        while True:
            await loop.run_in_executor(
                executor,
                self._setup(),
                )
            await asyncio.sleep(self.timeout)


if __name__ == '__main__':
    server1 = AsyncModbusServer(
        host='127.0.0.1',
        bit_adr=0,
        bit_num=16,
        word_adr=0,
        word_num=5,
        name='Server1',
    )
    asyncio.get_event_loop().run_until_complete(server1.run_task())
    asyncio.get_event_loop().run_forever()
