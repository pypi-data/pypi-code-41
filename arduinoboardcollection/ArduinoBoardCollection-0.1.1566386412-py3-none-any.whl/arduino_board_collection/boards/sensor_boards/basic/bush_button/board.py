from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator import basic_types as at
from ArduinoCodeCreator.statements import for_, if_, else_
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    BasicBoardModule,
    ArduinoBoard,
)
from arduino_controller.arduino_variable import arduio_variable


class PushButtoModule(ArduinoBoardModule):
    # depencies
    basic_board_module = BasicBoardModule

    # arduino_variables
    button_pin = arduio_variable(
        name="button_pin", arduino_data_type=uint8_t, eeprom=True
    )
    button_pressed = arduio_variable(
        name="button_pressed",
        arduino_data_type=bool_,
        setter=False,
        arduio_setter=False,
        is_data_point=True,
    )
    reinitalize_button = at.Function("reinitalize_button", uint8_t)
    reinitalize_button.add_call(Arduino.pinMode(reinitalize_button.arg1, Arduino.INPUT))

    def instance_arduino_code(self, ad):
        ad.setup.add_call(self.reinitalize_button(self.button_pin))
        self.button_pin.arduino_setter.add_call(
            self.reinitalize_button(self.button_pin)
        )

        ad.loop.add_call(
            if_(
                Arduino.digitalRead(self.button_pin) == Arduino.HIGH,
                self.button_pressed.set(Arduino.true),
            ),
            else_(self.button_pressed.set(Arduino.false)),
        )


class PushButtonBoard(ArduinoBoard):
    FIRMWARE = 12635865944940492681
    modules = [PushButtoModule]


if __name__ == "__main__":
    ins = PushButtonBoard()
    ins.create_ino()
