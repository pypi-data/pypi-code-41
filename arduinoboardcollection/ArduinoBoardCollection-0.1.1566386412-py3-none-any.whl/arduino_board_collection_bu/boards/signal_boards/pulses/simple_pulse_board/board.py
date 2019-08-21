from ArduinoCodeCreator.arduino_data_types import *
from arduino_controller.basicboard.board import ArduinoBasicBoard
from arduino_controller.arduino_variable import arduio_variable


class SimplePulseBoard(ArduinoBasicBoard):
    FIRMWARE = 15627604053828192
    CLASSNAME = "Simple Pulse Board"
    PULSE_TYPE_SQUARE = 0
    PULSE_TYPE_SINE = 1
    PULSEPIN = 6

    pulse_type = arduio_variable(
        name="pulse_type",
        default=PULSE_TYPE_SINE,
        maximum=1,
        allowed_values={PULSE_TYPE_SQUARE: "square", PULSE_TYPE_SINE: "sine"},
        eeprom=True,
    )

    pulse_pin = arduio_variable(
        name="pulse_pin", arduino_data_type=uint8_t, eeprom=True
    )

    wavelength = arduio_variable(
        name="wavelength", arduino_data_type=uint16_t, minimum=1, default=1000
    )  # in millisec
    current_val = arduio_variable(
        name="current_val", arduino_data_type=uint16_t, is_data_point=True, save=False
    )  # in mV
    running = arduio_variable(name="pulsing", arduino_data_type=bool_)

    def __init__(self):
        super().__init__()

    def get_frequency(self):
        return 1000 / self.wavelength

    def set_frequency(self, hertz):
        self.wavelength = 1000 / hertz

    frequency = property(get_frequency, set_frequency)


#
# class SimplePulseBoardArduinoData(ArduinoData):
#
#     pulse_pos = ArduinoDataGlobalVariable("pulse_pos", ArduinoDataTypes.double, 0)
#     max_current_val = ArduinoDataGlobalVariable("max_current_val", ArduinoDataTypes.uint16_t, -1)
#
#     def __init__(self, board_instance):
#         super().__init__(board_instance)
#         self.loop_function = ArduinoLoopFunction(
#             ArduinoDataFunction.if_condition(
#                 board_instance.get_module_var_by_name("running").name,
#                 self.pulse_pos.code_set(ArduinoDataFunction.divide(
#                     ArduinoDataFunction.mod(ArduinoBasicBoardArduinoData.ct,board_instance.get_module_var_by_name("wavelength").name),
#                     ArduinoDataFunction.multiply(float(1.0),board_instance.get_module_var_by_name("wavelength").name)
#                 ))+
#                 ArduinoDataFunction.if_condition(
#                     ArduinoDataFunction.equal(board_instance.get_module_var_by_name("pulse_type").name,board_instance.PULSE_TYPE_SQUARE),
#                     ArduinoDataFunction.if_condition(ArduinoDataFunction.lesser_equal_than(self.pulse_pos,0.5),
#                                                      ArduinoDataFunction.set_variable(board_instance.get_module_var_by_name("current_val").name,self.max_current_val)
#                                                      )+
#                     ArduinoDataFunction.else_condition(ArduinoDataFunction.set_variable(board_instance.get_module_var_by_name("current_val").name,0))
#                 )+
#                 ArduinoDataFunction.elseif_condition(
#                     ArduinoDataFunction.equal(board_instance.get_module_var_by_name("pulse_type").name,board_instance.PULSE_TYPE_SINE),
#                     ArduinoDataFunction.set_variable(board_instance.get_module_var_by_name("current_val").name,
#                                                      ArduinoDataFunction.multiply(self.max_current_val,
#                                                                         ArduinoDataFunction.divide(
#                                                                             ArduinoDataFunction.add(1,
#                                                                                                     ArduinoDataFunction.sin(
#                                                                                                         ArduinoDataFunction.multiply(2,self.pulse_pos,ArduinoDataFunction.PI())
#                                                                                                     ))
#                                                                         ,2)
#                                                      )
#                                                      )
#                 )+
#                 ArduinoDataFunction.analog_write(board_instance.PULSEPIN,
#                                                  ArduinoDataFunction.map(board_instance.get_module_var_by_name("current_val").name,0,self.max_current_val,0,255)
#                                                  )
#             )
#
#         )

if __name__ == "__main__":
    ins = SimplePulseBoard()
    ins.create_ino()
