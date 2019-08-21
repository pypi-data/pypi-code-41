from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.statements import if_, else_
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    ArduinoBoard,
    BasicBoardModule,
)
from ArduinoCodeCreator.arduino_data_types import *
from arduino_controller.arduino_variable import arduio_variable


class RelayBoardModule(ArduinoBoardModule):
    basic_board_module = BasicBoardModule

    relay_pin = arduio_variable(
        name="relay_pin", arduino_data_type=uint8_t, eeprom=True
    )
    active = arduio_variable(
        name="active", arduino_data_type=bool_, is_data_point=True, save=False
    )

    def instance_arduino_code(self, ad):
        ad.setup.add_call(Arduino.pinMode(self.relay_pin, Arduino.OUTPUT))
        ad.loop.add_call(
            if_(self.active, Arduino.digitalWrite(self.relay_pin, Arduino.LOW)),
            else_(Arduino.digitalWrite(self.relay_pin, Arduino.HIGH)),
        )
        self.relay_pin.arduino_setter.add_call(
            Arduino.pinMode(self.relay_pin, Arduino.OUTPUT)
        )


class RelayBoard(ArduinoBoard):
    FIRMWARE = 15650246521463158
    modules = [RelayBoardModule]


if __name__ == "__main__":
    ins = RelayBoard()
    ins.create_ino()
