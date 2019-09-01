# import the server implementation
from pymodbus.client.sync import ModbusSerialClient as ModbusClient,ModbusTcpClient
from pymodbus.mei_message import *
#from registers import registerByName


#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
import logging
_logger = logging.getLogger(__name__)

class EPsolarTracerClient:
    ''' EPsolar Tracer client
    '''

    def __init__(self, unit = 1, serialclient = None, **kwargs):
        ''' Initialize a serial client instance
        '''
        self.unit = unit
        if serialclient == None:
            port = kwargs.get('port', '/dev/ttyUSB1')
            baudrate = kwargs.get('baudrate', 115200)
            self.client = ModbusTcpClient('192.168.130.10', port=26)#ModbusClient(method = 'rtu', port = port, baudrate = baudrate, kwargs = kwargs)

        else:
            self.client = serialclient

    def connect(self):
        ''' Connect to the serial
        :returns: True if connection succeeded, False otherwise
        '''
        return self.client.connect()

    def close(self):
        ''' Closes the underlying connection
        '''
        return self.client.close()

    def read_device_info(self):
        request = ReadDeviceInformationRequest (unit = self.unit)
        response = self.client.execute(request)
        return response

    def read_input(self, register):
        #register = registerByName(name)
        if register.bits:
            response = self.client.read_discrete_inputs(register.address, register.count, unit = self.unit)
            return register.decode_bits(response)
        elif register.is_coil():
            response = self.client.read_coils(register.address, register.count, unit = self.unit)
        elif register.is_discrete_input():
            response = self.client.read_discrete_inputs(register.address, register.count, unit = self.unit)

        elif register.is_input_register():
            response = self.client.read_input_registers(register.address, register.count, unit = self.unit)
        else:
            response = self.client.read_holding_registers(register.address, register.count, unit = self.unit)
        return register.decode(response)

    def write_output(self, register, value):
        #register = registerByName(name)
        values = register.encode(value)
        response = False
        if register.is_coil():
            self.client.write_coil(register.address, values, unit = self.unit)
            response = True
        elif register.is_discrete_input():
            _logger.error("Cannot write discrete input " + repr(register.name))
            pass
        elif register.is_input_register():
            _logger.error("Cannot write input register " + repr(register.name))
            pass
        else:
            self.client.write_registers(register.address, values, unit = self.unit)
            response = True
        return response
