# -*- coding: utf-8 -*-

"""Async modbus client."""

from modbus2websocket import async_modbus_client as modbus
from modbus2websocket import async_websocket_server as ws
import asyncio


class Router(object):
    """Router class."""

    reg_tuple = ('hr', 'c', 'di', 'ir')

    def __init__(self, ws_host, ws_port, modbus_host):
        """Init router. Queue used for data exchange."""
        self.queue = asyncio.Queue(maxsize=1)
        self.websocketServer = ws.AsyncWsClient(
            queue=self.queue,
            host=ws_host,
            port=ws_port,
        )
        self.client = modbus.AsyncModbusClient(
            queue=self.queue,
            host=modbus_host,
            )

    def add_modbus_reg(self, reg_list):
        """Define registers to read."""
        for reg in reg_list:
            for key in reg:
                if key not in Router.reg_tuple:
                    raise modbus.ModbusClientError('Wrong register type.')
                adr = reg[key]['adr']
                num = reg[key]['num']
                name = reg[key]['name']
                self.client.add_registers(key, adr, num, name)

    def run(self):
        """Run loop FOREVER."""
        tasks = []
        tasks.append(self.client.run_task())
        tasks.append(self.websocketServer.run_task())
        loop = asyncio.get_event_loop()
        wait_tasks = asyncio.wait(tasks)
        loop.run_until_complete(wait_tasks)
        loop.run_forever()


if __name__ == '__main__':
    ws_ip = '127.0.0.1'
    ws_port = 8888
    modbus_ip = '127.0.0.1'
    router = Router(ws_ip, ws_port, modbus_ip)
    regs = {
        'hr':
        {
            'adr': 0,
            'num': 10,
            'name': 'Reg1',
        },
        'di':
        {
            'adr': 0,
            'num': 10,
            'name': 'DI1',
        },
    }
    router.add_modbus_reg(regs)
    router.run()
