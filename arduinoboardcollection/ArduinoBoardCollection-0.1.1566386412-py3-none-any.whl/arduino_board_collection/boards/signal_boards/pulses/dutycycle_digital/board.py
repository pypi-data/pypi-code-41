from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.basic_types import Variable
from ArduinoCodeCreator.statements import if_, else_, elseif_
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    ArduinoBoard,
    BasicBoardModule,
)
from ArduinoCodeCreator.arduino_data_types import *
from arduino_controller.arduino_variable import arduio_variable


class DutyCycleBoardModule(ArduinoBoardModule):
    basic_board_module = BasicBoardModule

    signal_pin = arduio_variable(
        name="signal_pin", arduino_data_type=uint8_t, eeprom=True
    )
    full_cycle = arduio_variable(
        name="full_cycle", arduino_data_type=uint32_t, eeprom=True
    )
    duty_cycle = arduio_variable(
        name="duty_cycle",
        arduino_data_type=float_,
        minimum=0,
        maximum=100,
        html_attributes={"step": 0.1},
        save=False,
    )

    last_cycle = Variable("last_cycle", uint32_t, 0)
    cycletime = Variable("cycletime", uint32_t, 0)

    def instance_arduino_code(self, ad):
        ad.setup.add_call(Arduino.pinMode(self.signal_pin, Arduino.OUTPUT))

        ad.loop.add_call(
            self.cycletime.set(self.basic_board_module.current_time - self.last_cycle),
            if_(
                self.cycletime > self.full_cycle,
                (
                    self.cycletime.set(0),
                    self.last_cycle.set(self.basic_board_module.current_time),
                ),
            ),
            if_(
                self.duty_cycle == 0,
                Arduino.digitalWrite(self.signal_pin, Arduino.HIGH),
            ),
            elseif_(
                self.duty_cycle == 100,
                Arduino.digitalWrite(self.signal_pin, Arduino.LOW),
            ),
            elseif_(
                self.cycletime
                < self.full_cycle
                * ((self.duty_cycle.cast(float_) / self.duty_cycle.maximum)),
                Arduino.digitalWrite(self.signal_pin, Arduino.LOW),
            ),
            else_(Arduino.digitalWrite(self.signal_pin, Arduino.HIGH)),
        )

        self.signal_pin.arduino_setter.add_call(
            Arduino.pinMode(self.signal_pin, Arduino.OUTPUT)
        )


class DutyCycleBoard(ArduinoBoard):
    FIRMWARE = 15657152897648263
    modules = [DutyCycleBoardModule]


if __name__ == "__main__":
    ins = DutyCycleBoard()
    ins.create_ino()
