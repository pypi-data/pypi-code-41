from arduino_board_collection.boards.controller_boards.motors.AccelStepperBoard.board import (
    AccelStepperBoardModule,
)
from arduino_board_collection.boards.sensor_boards.basic.hx711_board.board import (
    HX711Module,
)
from arduino_controller.basicboard.board import ArduinoBoard, ArduinoBoardModule


class TensileTestModule(ArduinoBoardModule):
    # depencies
    accel_stepper_module = AccelStepperBoardModule
    hx711_module = HX711Module


# lower_button_module = PushButtoModule
# upper_button_module = PushButtoModule

# def post_initalization(self):
# self.lower_button_module.button_pin.name = "lower_button_pin"
#  self.lower_button_module.button_pressed.name = "lower_button_pressed"
# self.lower_button_module.button_pressed.is_data_point = False
#  self.upper_button_module.button_pin.name = "upper_button_pin"
#   self.upper_button_module.button_pressed.name = "upper_button_pressed"
# self.upper_button_module.button_pressed.is_data_point = False

#  def instance_arduino_code(self, ad):
#   ad.loop.add_call(
#        if_(self.lower_button_module.button_pressed.or_(self.upper_button_module.button_pressed),
#            self.accel_stepper_module.stepper.stop()
#            )
#     )
class TensileTestBoard(ArduinoBoard):
    FIRMWARE = 17667236029856103160
    modules = [TensileTestModule]


if __name__ == "__main__":
    ins = TensileTestBoard()
    ins.create_ino()
