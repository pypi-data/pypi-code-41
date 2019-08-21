from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator.basic_types import Variable
from ArduinoCodeCreator.statements import for_
from arduino_controller.basicboard.board import ArduinoBasicBoard
from arduino_controller.arduino_variable import arduio_variable


class AnalogReadBoard(ArduinoBasicBoard):
    FIRMWARE = 13650142050147572

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

    avg = Variable("average", uint32_t, 0)

    def pre_ini_function(self):
        super().pre_ini_function()

    def add_arduino_code(self, ad):

        ad.setup.add_call(Arduino.analogReference(Arduino.EXTERNAL))

        ad.loop.add_call(
            self.avg.set(0),
            for_(
                for_.i,
                for_.i < self.samples,
                1,
                self.avg.set(self.avg + Arduino.analogRead(self.analog_pin)),
            ),
            self.analog_value.set(self.avg / self.samples),
        )

        self.analog_pin.arduino_setter.add_call(
            Arduino.pinMode(self.analog_pin, Arduino.INPUT)
        )


if __name__ == "__main__":
    ins = AnalogReadBoard()
    ins.create_ino()
