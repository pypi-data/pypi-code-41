from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.basic_types import Variable
from ArduinoCodeCreator.statements import if_, else_
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    ArduinoBoard,
    BasicBoardModule,
)
from ArduinoCodeCreator.arduino_data_types import *
from arduino_controller.arduino_variable import arduio_variable


class AnalogPuleBoard(ArduinoBoardModule):
    basic_board_module = BasicBoardModule

    pulse_pin = arduio_variable(
        name="pulse_pin", arduino_data_type=uint8_t, eeprom=True
    )

    full_cycle = arduio_variable(
        name="full_cycle", arduino_data_type=uint32_t, eeprom=True
    )
    duty_cycle = arduio_variable(
        name="duty_cycle",
        arduino_data_type=float_,
        is_data_point=True,
        minimum=0,
        maximum=1,
    )

    last_cycle = Variable("last_cycle", uint32_t, 0)
    cycletime = Variable("cycletime", uint32_t, 0)

    def instance_arduino_code(self, ad):
        ad.setup.add_call(Arduino.pinMode(self.relay_pin, Arduino.OUTPUT))

        ad.loop.add_call(
            self.cycletime.set(self.basic_board_module.current_time - self.last_cycle),
            if_(self.cycletime > self.full_cycle, self.cycletime.set(0)),
            if_(
                self.cycletime > self.full_cycle * self.duty_cycle,
                Arduino.digitalWrite(self.relay_pin, Arduino.HIGH),
            ),
            else_(Arduino.digitalWrite(self.relay_pin, Arduino.HIGH)),
        )

        self.relay_pin.arduino_setter.add_call(
            Arduino.pinMode(self.relay_pin, Arduino.OUTPUT)
        )


class AnalogPuleBoard(ArduinoBoard):
    FIRMWARE = 15657699897639596
    modules = [DutyCycleRelayBoardModule]


if __name__ == "__main__":
    ins = AnalogPuleBoard()
    ins.create_ino()
