from ArduinoCodeCreator.arduino import Arduino
from arduino_controller.basicboard.board import ArduinoBasicBoard
from ArduinoCodeCreator.arduino_data_types import *
from arduino_controller.arduino_variable import arduio_variable


class RelayBoard(ArduinoBasicBoard):
    FIRMWARE = 15650246521463158

    relay_pin = arduio_variable(
        name="relay_pin", arduino_data_type=uint8_t, eeprom=True
    )
    open = arduio_variable(name="open", arduino_data_type=bool_, is_data_point=True)

    def add_arduino_code(self, ad):
        ad.setup.add_call(Arduino.pinMode(self.relay_pin, Arduino.OUTPUT))
        ad.loop.add_call(Arduino.digitalWrite(self.relay_pin, self.open))
        self.relay_pin.arduino_setter.add_call(
            Arduino.pinMode(self.relay_pin, Arduino.OUTPUT)
        )


if __name__ == "__main__":
    ins = RelayBoard()
    ins.create_ino()
