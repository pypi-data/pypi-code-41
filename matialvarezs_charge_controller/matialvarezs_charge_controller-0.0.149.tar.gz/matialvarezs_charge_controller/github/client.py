# import the server implementation
from pymodbus.client.sync import ModbusSerialClient as ModbusClient,ModbusTcpClient
from pymodbus.mei_message import *
#from registers import registerByName
from matialvarezs_charge_controller import settings as matialvarezs_charge_controller_settings
from matialvarezs_node_configurations import utils as matialvarezs_node_configurations_utils
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
        if matialvarezs_charge_controller_settings.MODBUS_CLIENT_TYPE == 'TCP':
            self.client = ModbusTcpClient(matialvarezs_node_configurations_utils.get_or_none_configuration(key='charge_controller_modbus_tcp').value, port=26)#ModbusClient(method = 'rtu', port = port, baudrate = baudrate, kwargs = kwargs)
        elif matialvarezs_charge_controller_settings.MODBUS_CLIENT_TYPE == 'SERIAL':
            port = matialvarezs_charge_controller_settings.MODBUS_CLIENT_SERIAL_PORT
            self.client = ModbusClient(method='rtu', port=port, stopbits=2, bytesize=8, parity='N', baudrate=115200)
        else:
            pass

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
