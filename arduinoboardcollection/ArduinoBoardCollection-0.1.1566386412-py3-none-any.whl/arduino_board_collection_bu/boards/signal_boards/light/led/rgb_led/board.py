from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import uint8_t
from arduino_controller.basicboard.board import ArduinoBasicBoard
from arduino_controller.arduino_variable import arduio_variable


class RgbLed(ArduinoBasicBoard):
    FIRMWARE = 15633540938822172

    LED_PIN_RED = 3
    LED_PIN_GREEN = 5
    LED_PIN_BLUE = 6

    red = arduio_variable(name="red", arduino_data_type=uint8_t)
    green = arduio_variable(name="green", arduino_data_type=uint8_t)
    blue = arduio_variable(name="blue", arduino_data_type=uint8_t)

    red_pin = arduio_variable(name="red_pin", arduino_data_type=uint8_t, eeprom=True)
    green_pin = arduio_variable(
        name="green_pin", arduino_data_type=uint8_t, eeprom=True
    )
    blue_pin = arduio_variable(name="blue_pin", arduino_data_type=uint8_t, eeprom=True)

    def add_arduino_code(self, ad):
        ad.loop.add_call(
            Arduino.analogWrite(self.red_pin, self.red),
            Arduino.analogWrite(self.green_pin, self.green),
            Arduino.analogWrite(self.blue_pin, self.blue),
        )

        self.blue_pin.arduino_setter.prepend_call(Arduino.analogWrite(self.blue_pin, 0))
        self.blue_pin.arduino_setter.add_call(
            Arduino.pinMode(self.blue_pin, Arduino.OUTPUT)
        )

        self.red_pin.arduino_setter.prepend_call(Arduino.analogWrite(self.red_pin, 0))
        self.red_pin.arduino_setter.add_call(
            Arduino.pinMode(self.red_pin, Arduino.OUTPUT)
        )

        self.green_pin.arduino_setter.prepend_call(
            Arduino.analogWrite(self.green_pin, 0)
        )
        self.green_pin.arduino_setter.add_call(
            Arduino.pinMode(self.green_pin, Arduino.OUTPUT)
        )


if __name__ == "__main__":
    ins = RgbLed()
    ins.create_ino()
