from ArduinoCodeCreator.arduino import *
from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator.basic_types import *
from ArduinoCodeCreator.statements import *
from arduino_controller.arduino_variable import arduio_variable
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    BasicBoardModule,
    ArduinoBoard,
)
from arduino_controller.python_variable import python_variable


class AnalogReadModule(ArduinoBoardModule):
    # depencies
    basic_board_module = BasicBoardModule

    # arduino_variables
    samples = arduio_variable(name="samples", arduino_data_type=uint8_t, eeprom=True)
    analog_value = arduio_variable(
        name="analog_value",
        arduino_data_type=uint16_t,
        arduino_setter=False,
        is_data_point=True,
        save=False,
    )
    analog_pin = arduio_variable(
        name="analog_pin", arduino_data_type=uint8_t, eeprom=True
    )

    average = Variable("average", uint32_t, 0)

    def instance_arduino_code(self, ad):
        ad.loop.add_call(
            Arduino.analogRead(self.analog_pin),
            Arduino.delay(10),
            self.average.set(0),
            for_(
                for_.i,
                for_.i < self.samples,
                1,
                self.average.set(self.average + Arduino.analogRead(self.analog_pin)),
            ),
            self.analog_value.set(self.average / self.samples),
        )
        self.analog_pin.arduino_setter.add_call(
            Arduino.pinMode(self.analog_pin, Arduino.INPUT)
        )


class AnalogReadBoard(ArduinoBoard):
    FIRMWARE = 13650142050147572
    modules = [AnalogReadModule]


if __name__ == "__main__":
    ins = AnalogReadBoard()
    ins.create_ino()
