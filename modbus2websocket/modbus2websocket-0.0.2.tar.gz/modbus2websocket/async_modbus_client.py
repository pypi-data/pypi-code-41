# -*- coding: utf-8 -*-

"""Async modbus client."""

from pyModbusTCP.client import ModbusClient
import asyncio
import concurrent


class ModbusClientError(Exception):
    """Async Client Error Exceptions."""

    pass


class AsyncModbusClient(object):
    """Asyncio Modbus client."""

    max_adr = 65535
    max_number = 2000

    def __init__(self, *, queue=None, host='127.0.0.1'):
        """
        Init class.

        ::host:: str - By default client runs on localhost.
        ::port:: int - Port 502 is constant for ModdbusTCP.

        """
        self.queue = queue
        self.host = host
        self.port = 502
        self.client = ModbusClient(host=self.host, port=self.port)
        self.func_read_dict = {
            'hr': self.client.read_holding_registers,
            'c':  self.client.read_coils,
            'di': self.client.read_discrete_inputs,
            'ir': self.client.read_input_registers,
        }
        self.func_write_dict = {
            'hr': self.client.write_multiple_registers,
            'c':  self.client.write_multiple_coils,
        }
        self.registers_dict = {}
        self.reg_current_value = {}

    @classmethod
    def validate_adr(cls, adr):
        """Validate address."""
        if 0 <= adr <= AsyncModbusClient.max_adr:
            return adr
        raise ModbusClientError('Address wrong value: from 0 to 65535.')

    @classmethod
    def validate_num(cls, num):
        """Validate number."""
        if 1 <= num <= AsyncModbusClient.max_number:
            return num
        raise ModbusClientError('Number wrong value: from 1 to 2000.')

    @classmethod
    def validate_write(cls, write):
        """Validate write."""
        if 0 <= write <= 1:
            return write
        raise ModbusClientError('Value ::write:: should be 0 or 1.')

    def add_registers(self, reg_type, adr, num, name, write=0):
        """
        Add register to the Modbus Client.

        ::reg_type::    str - values from 'hr', 'di', 'c' or 'ir',
        ::adr::         int - value starting from 0 to 65535
        (AsyncModbusClient.max_adr),
        ::number::      int - from 1 to 2000 (AsyncModbusClient.max_number),
        ::name::        str - any unique name
        ::write::       int - 0 for reading, 1 for writing.
        """
        adr = AsyncModbusClient.validate_adr(adr)
        num = AsyncModbusClient.validate_num(num)
        write = AsyncModbusClient.validate_write(write)
        if write:
            pass  # Not implemented yet
        else:
            try:
                self.func_read_dict.set_default(
                    self.func_read_dict[reg_type],
                    [],
                    ).append({
                        'adr': adr,
                        'num': num,
                        'name': name,
                    })
            except Exception as err:
                raise ModbusClientError('Wrong modbus register type.', err)

    async def run_task(self):
        """Run asyncio client."""
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=3,
        )
        task = asyncio.create_task(self._awaitable(executor))
        await task

    def _read_reg(self):
        self.read_regs = {}
        for func in self.registers_dict:
            for reg in self.registers_dict[func]:
                adr = reg['adr']
                num = reg['num']
                name = reg['name']
                reg_func = func(adr, num)
                if name in self.read_regs:
                    raise Exception(
                        """Name {0} is not unique. Create unique name.
                        """.format(name),
                    )
                self.read_regs[name] = reg_func
        return self.read_regs

    async def _awaitable(self, executor):
        loop = asyncio.get_event_loop()
        while True:
            if self.client.is_open():
                self.reg_current_value = await loop.run_in_executor(
                    executor,
                    self._read_reg,
                )

            else:
                self.reg_current_value = 'Lost connection with Modbus server'
                self.client.open()

            if self.queue:
                await self.queue.put(self.reg_current_value)
            await asyncio.sleep(1)


if __name__ == '__main__':
    queue = asyncio.Queue()
    client = AsyncModbusClient(queue=queue, host='127.0.0.1')
    client.add_registers('hr', 0, 10, 'Reg1')
    client.add_registers('di', 0, 10, 'Reg2')
    client.add_registers('c', 5, 10, 'Reg3')
    asyncio.get_event_loop().run_until_complete(client.run_task())
    asyncio.get_event_loop().run_forever()
