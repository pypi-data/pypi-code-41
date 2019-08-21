from ArduinoCodeCreator.arduino_data_types import *
from arduino_board_collection.boards.controller_boards.basic.pid.board import PIDModule
from arduino_board_collection.boards.sensor_boards.thermal.max6675.board import (
    Max6675BoardModule,
)
from arduino_board_collection.boards.signal_boards.pulses.dutycycle_digital.board import (
    DutyCycleBoardModule,
)
from arduino_controller.basicboard.board import ArduinoBoard, ArduinoBoardModule
from arduino_controller.python_variable import python_variable


class RelayMax6675BangBangModule(ArduinoBoardModule):
    max6675 = Max6675BoardModule
    relay = DutyCycleBoardModule
    pid = PIDModule

    target_temperature = python_variable(
        "target_temperature", type=np.float, default=300.0
    )
    max_temperature = python_variable(
        "max_temperature", type=np.float, default=300, minimum=0
    )
    min_temperature = python_variable("min_temperature", type=np.float)

    running = python_variable("running", type=np.bool, default=False, save=False)

    def post_initalization(self):
        self.max6675.temperature.data_point_modification(self.bang_bang_temperature)
        self.relay.duty_cycle.is_data_point = True
        self.relay.duty_cycle.changeable = False
        self.pid.minimum = self.relay.duty_cycle.minimum
        self.pid.maximum = self.relay.duty_cycle.maximum

    def bang_bang_temperature(self, data):
        self.pid.current = data
        self.pid.target = self.target_temperature
        if self.running:
            pid = self.pid.pid()
            if pid is None:
                pid = 0
            self.relay.duty_cycle = pid
        else:
            self.pid.reset()
            self.relay.duty_cycle = 0
        return data


class RelayMax6675BangBangBoard(ArduinoBoard):
    FIRMWARE = 15657144496468016
    modules = [RelayMax6675BangBangModule]


if __name__ == "__main__":
    ins = RelayMax6675BangBangBoard()
    ins.create_ino()
