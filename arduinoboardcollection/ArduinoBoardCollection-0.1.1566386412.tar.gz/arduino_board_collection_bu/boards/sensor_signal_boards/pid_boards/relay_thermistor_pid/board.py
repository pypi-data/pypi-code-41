import time

from arduino_board_collection.boards.sensor_boards.thermal.thermistor.board import (
    ThermistorBoard,
)
from arduino_board_collection.boards.signal_boards.switches.relay.board import (
    RelayBoard,
)
from arduino_controller.basicboard.board import ArduinoBasicBoard
from ArduinoCodeCreator.arduino_data_types import *
from arduino_controller.arduino_variable import arduio_variable
from arduino_controller.python_variable import python_variable

try:
    _current_time = time.monotonic
except AttributeError:
    _current_time = time.time


def pdi_temperature(var, instance, data):
    var.default_setter(var, instance, data)
    if instance.running:
        on_time = instance.pid(data)
        print(on_time)
        if on_time is not None:
            if on_time > instance.threshold:
                instance.open = False
            else:
                instance.open = True
    else:
        instance.reset()


class RelayThermistorBoard(ThermistorBoard, RelayBoard):
    FIRMWARE = 15650261815701852
    target_temperature = python_variable(
        "target_temperature", type=np.float, default=298.15, minimum=0
    )
    max_temperature = python_variable(
        "max_temperature", type=np.float, default=500, minimum=0
    )
    min_temperature = python_variable(
        "min_temperature", type=np.float, default=0, minimum=0
    )

    max_on_time = 100
    min_on_time = 0
    threshold = python_variable(
        "threshold", type=np.float, default=50, minimum=0, maximum=100
    )
    running = python_variable("running", type=np.bool, default=False, save=False)
    kp = python_variable("kp", type=np.float, default=1)
    ki = python_variable("ki", type=np.float)
    kd = python_variable("kd", type=np.float)

    def __init__(self):
        super().__init__()
        self.get_module_var_by_name("temperature").setter = pdi_temperature
        self._last_time = _current_time()
        self._last_input = None
        self._integral = 0

    def reset(self):
        self._last_time = _current_time()
        self._last_input = None
        self._integral = 0

    def pid(self, input):
        if self._last_input is None:
            self._last_time = _current_time()
            time.sleep(0.01)
        now = _current_time()
        if now - self._last_time:
            dt = now - self._last_time
        else:
            return None
        error = self.target_temperature - input
        d_input = input - (self._last_input if self._last_input is not None else input)

        # compute integral and derivative terms
        proportional = self.kp * error
        self._integral += self.ki * error * dt
        self._integral = min(
            self.max_on_time, max(self.min_on_time, self._integral)
        )  # avoid integral windup

        derivative = -self.kd * d_input / dt

        # compute final output
        output = proportional + self._integral + derivative
        output = min(self.max_on_time, max(self.min_on_time, output))

        self._last_input = input
        self._last_time = now
        return output


if __name__ == "__main__":
    ins = RelayThermistorBoard()
    ins.create_ino()
