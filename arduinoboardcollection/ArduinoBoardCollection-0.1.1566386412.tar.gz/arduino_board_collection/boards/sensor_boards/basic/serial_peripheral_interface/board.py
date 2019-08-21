from ArduinoCodeCreator.arduino import Arduino, Eeprom
from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator import basic_types as at
from ArduinoCodeCreator.basic_types import Include
from ArduinoCodeCreator.statements import for_, if_, else_, return_
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    BasicBoardModule,
    ArduinoBoard,
)
from arduino_controller.arduino_variable import arduio_variable


class SPI(at.ArduinoClass):
    class_name = "SPI"
    include = "<SPI.h>"
    begin = at.Function("begin")
    transfer = at.Function("transfer", uint8_t, uint8_t)
    transfer16 = at.Function("transfer16", uint16_t, uint16_t)
    transferbuff = at.Function(
        "transfer", ((uint8_t_pointer, "buff"), (uint8_t, "size"))
    )


class SerialPeripheralInterfaceModule(ArduinoBoardModule):
    # depencies
    basic_board_module = BasicBoardModule
    unique = True
    # arduino_variables
    # sck = arduio_variable(name="sck", arduino_data_type=uint8_t, eeprom=True,default=13)
    # miso = arduio_variable(name="miso", arduino_data_type=uint8_t, eeprom=True,default=12)
    # mosi = arduio_variable(name="mosi", arduino_data_type=uint8_t, eeprom=True,default=11)
    spi = SPI()
    active_cs_pin = at.Variable(name="activate_cs_pin", type=uint8_t)
    deactivate_pin = at.Function("deactivate_pin")
    activate_pin = at.Function("activate_pin", uint8_t)
    read16 = at.Function("read16", uint8_t, uint16_t)

    @classmethod
    def module_arduino_code(cls, board, arduino_code_creator):
        cls.deactivate_pin.add_call(
            if_(
                cls.active_cs_pin > 0,
                code=(
                    Arduino.digitalWrite(cls.active_cs_pin, Arduino.HIGH),
                    cls.active_cs_pin.set(0),
                ),
            )
        )

        cls.activate_pin.add_call(
            if_(cls.active_cs_pin == cls.activate_pin.arg1, return_()),
            if_(cls.active_cs_pin > 0, cls.deactivate_pin()),
            Arduino.pinMode(cls.activate_pin.arg1, Arduino.OUTPUT),
            cls.active_cs_pin.set(cls.activate_pin.arg1),
            Arduino.digitalWrite(cls.active_cs_pin, Arduino.LOW),
        )

    def instance_arduino_code(self, arduino_code_creator):
        arduino_code_creator.setup.prepend_call(self.spi.begin())

        self.read16.add_call(
            self.activate_pin(self.read16.arg1),
            self.basic_board_module.dummy16.set(self.spi.transfer16(0)),
            self.deactivate_pin(),
            return_(self.basic_board_module.dummy16),
        )
