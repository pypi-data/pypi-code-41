from ArduinoCodeCreator.basic_types import ArduinoClass
from functools import partial

from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import *
from arduino_board_collection.boards.sensor_boards.basic.analog_read_board.board import (
    AnalogReadModule,
)
from arduino_board_collection.boards.sensor_boards.basic.serial_peripheral_interface.board import (
    SerialPeripheralInterfaceModule,
)
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    ArduinoBoard,
    BasicBoardModule,
)
from arduino_controller.arduino_variable import arduio_variable
from arduino_controller.python_variable import python_variable
from ArduinoCodeCreator import basic_types as at


class Max6675BoardModule(ArduinoBoardModule):
    spim = SerialPeripheralInterfaceModule
    temperature = arduio_variable(
        name="temperature",
        arduino_data_type=double_,
        arduino_setter=False,
        setter=None,
        is_data_point=True,
        save=False,
    )
    cs_pin = arduio_variable(name="cs_pin", arduino_data_type=uint8_t, eeprom=True)

    def instance_arduino_code(self, ad):
        self.spim.basic_board_module.dataloop.prepend_call(
            self.temperature.set((self.spim.read16(self.cs_pin) >> 3) * 0.25 + 273.15)
        )


class Max6675Board(ArduinoBoard):
    FIRMWARE = 15340959432412641196
    modules = [Max6675BoardModule]


if __name__ == "__main__":
    ins = Max6675Board()
    ins.create_ino()
