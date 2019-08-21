from ArduinoCodeCreator.arduino_data_types import *
from arduino_board_collection.boards.sensor_boards.basic.analog_read_board2.board import (
    AnalogReadBoard2,
)
from arduino_board_collection.boards.sensor_boards.thermal.thermistor.board import (
    ThermistorBoard,
)
from arduino_controller.basicboard.board import ArduinoBasicBoard
from arduino_controller.arduino_variable import arduio_variable
from arduino_controller.python_variable import python_variable


def resistance_to_temperature(var, instance, data, send_to_board=True):
    var.default_setter(
        var=var, instance=instance, data=data, send_to_board=send_to_board
    )
    print(var)
    try:
        R2 = instance.reference_resistance * (1023.0 - data) / data
        logR2 = np.log(R2)
        T = 1.0 / (instance.a + instance.b * logR2 + instance.c * logR2 * logR2 * logR2)
        instance.temperature = T
    except ZeroDivisionError:
        pass


class ThermistorBoard2(ThermistorBoard, AnalogReadBoard2):
    FIRMWARE = 15650180050147573

    thermistor_base_resistance2 = arduio_variable(
        name="thermistor_base_resistance2",
        arduino_data_type=uint32_t,
        eeprom=True,
        default=10 ** 5,
    )
    reference_resistance2 = arduio_variable(
        name="reference_resistance2",
        arduino_data_type=uint32_t,
        eeprom=True,
        default=10 ** 5,
    )

    temperature2 = python_variable(
        "temperature2", type=np.float, changeable=False, is_data_point=True, save=False
    )
    reference_temperature2 = python_variable(
        "reference_temperature2", type=np.float, default=298.15, minimum=0
    )

    a2 = python_variable("a2", type=np.float, default=1.009249522e-03)
    b2 = python_variable("b2", type=np.float, default=2.378405444e-04)
    c2 = python_variable("c2", type=np.float, default=2.019202697e-07)

    def pre_ini_function(self):
        super().pre_ini_function()
        self.thermistor_base_resistance.name = (
            self.thermistor_base_resistance.name + "1"
        )
        self.reference_resistance.name = self.reference_resistance.name + "1"
        self.temperature.name = self.temperature.name + "1"
        self.reference_temperature.name = self.reference_temperature.name + "1"
        self.a.name = self.a.name + "1"
        self.b.name = self.b.name + "1"
        self.c.name = self.c.name + "1"

        self.analog_value2.name = self.analog_value.name + "2"
        self.analog_value.name = self.analog_value.name + "1"

        self.analog_value2.setter = self.resistance_to_temperature2

    @staticmethod
    def resistance_to_temperature2(var, instance, data, send_to_board=True):
        var.default_setter(
            var=var, instance=instance, data=data, send_to_board=send_to_board
        )
        try:
            R2 = instance.reference_resistance2 * (1023.0 - data) / data
            logR2 = np.log(R2)
            T = 1.0 / (
                instance.a2 + instance.b2 * logR2 + instance.c2 * logR2 * logR2 * logR2
            )
            instance.temperature2 = T
        except ZeroDivisionError:
            pass


if __name__ == "__main__":
    ins = ThermistorBoard2()
    ins.create_ino()
