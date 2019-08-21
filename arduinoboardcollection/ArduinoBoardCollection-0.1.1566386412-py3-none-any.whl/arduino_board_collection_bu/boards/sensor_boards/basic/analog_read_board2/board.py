from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator.basic_types import Variable
from ArduinoCodeCreator.statements import for_
from arduino_board_collection.boards.sensor_boards.basic.analog_read_board.board import (
    AnalogReadBoard,
)
from arduino_controller.basicboard.board import ArduinoBasicBoard
from arduino_controller.arduino_variable import arduio_variable


class AnalogReadBoard2(AnalogReadBoard):
    FIRMWARE = 13650142050147573

    samples = arduio_variable(name="samples", arduino_data_type=uint8_t, eeprom=True)

    analog_value2 = arduio_variable(
        name="analog_value2",
        arduino_data_type=uint16_t,
        arduino_setter=False,
        is_data_point=True,
        save=False,
    )
    analog_pin2 = arduio_variable(
        name="analog_pin2", arduino_data_type=uint8_t, eeprom=True
    )

    def pre_ini_function(self):
        super().pre_ini_function()
        self.analog_value.name = "analog_value1"
        self.analog_pin.name = "analog_pin1"

    def add_arduino_code(self, ad):

        ad.loop.add_call(
            self.avg.set(0),
            for_(
                for_.i,
                for_.i < self.samples,
                1,
                self.avg.set(self.avg + Arduino.analogRead(self.analog_pin2)),
            ),
            self.analog_value2.set(self.avg / self.samples),
        )

        self.analog_pin2.arduino_setter.add_call(
            Arduino.pinMode(self.analog_pin2, Arduino.INPUT)
        )


if __name__ == "__main__":
    ins = AnalogReadBoard2()
    ins.create_ino()
