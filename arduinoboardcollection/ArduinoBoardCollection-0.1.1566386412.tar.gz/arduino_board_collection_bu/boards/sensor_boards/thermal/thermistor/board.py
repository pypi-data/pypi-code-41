from ArduinoCodeCreator.arduino_data_types import *
from arduino_board_collection.boards.sensor_boards.basic.analog_read_board.board import (
    AnalogReadBoard,
)
from arduino_controller.basicboard.board import ArduinoBasicBoard
from arduino_controller.arduino_variable import arduio_variable
from arduino_controller.python_variable import python_variable


class ThermistorBoard(AnalogReadBoard):
    FIRMWARE = 15650180050147572

    thermistor_base_resistance = arduio_variable(
        name="thermistor_base_resistance",
        arduino_data_type=uint32_t,
        eeprom=True,
        default=10 ** 5,
    )
    reference_resistance = arduio_variable(
        name="reference_resistance",
        arduino_data_type=uint32_t,
        eeprom=True,
        default=10 ** 5,
    )

    temperature = python_variable(
        "temperature", type=np.float, changeable=False, is_data_point=True, save=False
    )
    reference_temperature = python_variable(
        "reference_temperature", type=np.float, default=298.15, minimum=0
    )

    a = python_variable("a", type=np.float, default=1.009249522e-03)
    b = python_variable("b", type=np.float, default=2.378405444e-04)
    c = python_variable("c", type=np.float, default=2.019202697e-07)

    def pre_ini_function(self):
        super().pre_ini_function()
        self.analog_value.name = "thermistor_resistance"
        self.analog_value.setter = self.resistance_to_temperature

    @staticmethod
    def resistance_to_temperature(var, instance, data, send_to_board=True):
        var.default_setter(
            var=var, instance=instance, data=data, send_to_board=send_to_board
        )
        try:
            R2 = instance.reference_resistance * (1023.0 - data) / data
            logR2 = np.log(R2)
            T = 1.0 / (
                instance.a + instance.b * logR2 + instance.c * logR2 * logR2 * logR2
            )
            instance.temperature = T
        except ZeroDivisionError:
            pass


if __name__ == "__main__":
    ins = ThermistorBoard()
    ins.create_ino()
