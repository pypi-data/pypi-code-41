from functools import partial

from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import *
from arduino_board_collection.boards.sensor_boards.basic.analog_read_board.board import (
    AnalogReadModule,
)
from arduino_controller.basicboard.board import ArduinoBoardModule, ArduinoBoard
from arduino_controller.arduino_variable import arduio_variable
from arduino_controller.python_variable import python_variable


class ThermistorBoardModule(ArduinoBoardModule):
    analog_read_module = AnalogReadModule

    # analog_read_module.analog_value.is_data_point = False

    # arduino_variables
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

    # python_variables
    temperature = python_variable(
        "temperature", type=np.float, changeable=False, is_data_point=True, save=False
    )
    reference_temperature = python_variable(
        "reference_temperature", type=np.float, default=298.15, minimum=0
    )

    b = python_variable("b", type=np.uint32, default=4000)
    # a = python_variable("a", type=np.float,default=1.009249522)
    # b = python_variable("b", type=np.float,default=2.378405444)
    # c = python_variable("c", type=np.float,default=2.019202697)

    @classmethod
    def module_arduino_code(cls, board, arduino_code_creator):
        arduino_code_creator.setup.add_call(Arduino.analogReference(Arduino.EXTERNAL))

    def post_initalization(self):
        self.analog_read_module.analog_value.data_point_modification(
            self.resistance_to_temperature
        )

    def resistance_to_temperature(self, data):
        try:
            R2 = self.reference_resistance * data / (1023.0 - data)
            Tk = R2 / self.thermistor_base_resistance
            Tk = np.log(Tk)
            Tk /= self.b
            Tk += 1 / self.reference_temperature
            Tk = 1 / Tk
            self.temperature = Tk
        except ZeroDivisionError:
            pass
        return data

        # try:
        #     R2 = self.reference_resistance*data/ (1023.0-data)
        #     print(R2)
        #     logR2 = np.log(R2)
        #     Tk = (1.0 / (self.a/10**3 + self.b*logR2/10**4 + self.c*logR2*logR2*logR2/10**7))
        #     self.temperature = Tk
        # except ZeroDivisionError:
        #     pass


class ThermistorBoard(ArduinoBoard):
    FIRMWARE = 15650180050147572
    modules = [ThermistorBoardModule]


class DualThermistorBoard(ArduinoBoard):
    FIRMWARE = 15650180050147573
    modules = [ThermistorBoardModule, ThermistorBoardModule]


if __name__ == "__main__":
    ins = DualThermistorBoard()
    ins.create_ino()
