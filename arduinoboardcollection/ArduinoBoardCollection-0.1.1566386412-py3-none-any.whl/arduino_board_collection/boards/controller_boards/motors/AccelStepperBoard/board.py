from ArduinoCodeCreator import basic_types as at
from ArduinoCodeCreator.arduino import Arduino
from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator.statements import while_
from arduino_controller.arduino_variable import arduio_variable
from arduino_controller.basicboard.board import (
    ArduinoBoardModule,
    ArduinoBoard,
    BasicBoardModule,
)


class AccelStepper(at.ArduinoClass):
    class_name = "AccelStepper"
    motor_interface_type = at.ArduinoEnum(
        "MotorInterfaceType",
        {
            0: (
                "FUNCTION",
                "Use the functional interface, implementing your own driver functions (internal use only)",
            ),
            1: ("DRIVER", "Stepper Driver, 2 driver pins required"),
            2: ("FULL2WIRE", "2 wire stepper, 2 motor pins required"),
            3: (
                "FULL3WIRE",
                "3 wire stepper, such as HDD spindle, 3 motor pins required",
            ),
            4: ("FULL4WIRE", "4 wire full stepper, 4 motor pins required"),
            6: (
                "HALF3WIRE",
                "3 wire half stepper, such as HDD spindle, 3 motor pins required",
            ),
            8: ("HALF4WIRE", "4 wire half stepper, 4 motor pins required)"),
        },
    )

    # void    moveTo(long absolute);
    moveTo = at.Function("moveTo", long_)
    # void    move(long relative);
    run = at.Function("run", return_type=bool_)
    # runSpeed = at.Function("runSpeed",return_type=bool_)
    setMaxSpeed = at.Function("setMaxSpeed", float_)
    # float 	maxSpeed ()
    setAcceleration = at.Function("setAcceleration", float_)
    # void    setSpeed(float speed);
    # float   speed();
    # long    distanceToGo();
    # long    targetPosition();
    currentPosition = at.Function("currentPosition", return_type=long_)
    setCurrentPosition = at.Function("setCurrentPosition", long_)
    # void    runToPosition();
    # boolean runSpeedToPosition();
    # void    runToNewPosition(long position);
    stop = at.Function("stop")
    # void 	setMinPulseWidth (unsigned int minWidth)
    setEnablePin = at.Function("setEnablePin", long_)
    # void 	setPinsInverted (bool directionInvert=false, bool stepInvert=false, bool enableInvert=false)
    # void 	setPinsInverted (bool pin1Invert, bool pin2Invert, bool pin3Invert, bool pin4Invert, bool enableInvert)
    # bool 	isRunning ()

    disableOutputs = at.Function("disableOutputs")
    enableOutputs = at.Function("enableOutputs")

    include = "<AccelStepper.h>"


class AccelStepperBoardModule(ArduinoBoardModule):
    # depencies
    basic_board_module = BasicBoardModule

    accel_stepper = AccelStepper()
    stepPin = arduio_variable(
        name="stepPin", arduino_data_type=uint8_t, eeprom=True, default=2
    )
    dirPin = arduio_variable(
        name="dirPin", arduino_data_type=uint8_t, eeprom=True, default=3
    )
    enablePin = arduio_variable(
        name="enablePin", arduino_data_type=uint8_t, eeprom=True, default=4
    )

    stepper = accel_stepper("stepper")

    reinitalize_stepper = at.Function("reinitalize_stepper")
    max_steps_per_loop = arduio_variable(
        name="max_steps_per_loop",
        arduino_data_type=uint8_t,
        eeprom=True,
        default=1,
        minimum=1,
    )

    steps_per_mm = arduio_variable(
        "steps_per_mm", uint16_t, eeprom=True, default=200, minimum=1
    )

    # step_per_mm_dependend
    stepper_max_speed = arduio_variable(
        name="stepper_max_speed",
        arduino_data_type=float_,
        eeprom=True,
        default=1000,
        minimum=0.01,
        html_attributes={"step": 0.01},
    )
    stepper_acceleration = arduio_variable(
        name="stepper_acceleration",
        arduino_data_type=float_,
        eeprom=True,
        default=10,
        minimum=0.01,
        html_attributes={"step": 0.01},
    )
    target_position = arduio_variable(
        name="target_position",
        arduino_data_type=float_,
        save=False,
        html_attributes={"step": 0.1},
    )
    stepper_current_position = arduio_variable(
        name="stepper_current_position",
        arduino_data_type=float_,
        default=0,
        save=True,
        is_data_point=True,
        html_attributes={"step": 0.1},
    )

    def instance_arduino_code(self, ad):
        self.stepper = self.accel_stepper(
            "stepper",
            AccelStepper.motor_interface_type["DRIVER"],
            self.stepPin,
            self.dirPin,
        )
        self.reinitalize_stepper.add_call(
            self.stepper.stop(),
            while_(self.stepper.run()),
            self.stepper.disableOutputs(),
            self.stepper.reinitalize(),
            self.stepper.setMaxSpeed(self.stepper_max_speed * self.steps_per_mm),
            self.stepper.setCurrentPosition(
                self.stepper_current_position * self.steps_per_mm
            ),
            self.stepper.setAcceleration(self.stepper_acceleration * self.steps_per_mm),
            self.stepper.setEnablePin(self.enablePin),
        )
        self.stepPin.arduino_setter.add_call(self.reinitalize_stepper())
        self.dirPin.arduino_setter.add_call(self.reinitalize_stepper())

        self.enablePin.arduino_setter.add_call(
            self.stepper.setEnablePin(self.enablePin)
        )

        ad.setup.add_call(self.reinitalize_stepper())

        self.stepper_current_position.arduino_setter.add_call(
            self.stepper.setCurrentPosition(
                self.stepper_current_position * self.steps_per_mm
            )
        )
        self.stepper_current_position.arduino_getter.prepend_call(
            self.stepper_current_position.set(
                self.stepper.currentPosition() / self.steps_per_mm.cast(float_)
            )
        )

        self.stepper_max_speed.arduino_setter.add_call(
            self.stepper.setMaxSpeed(self.stepper_max_speed * self.steps_per_mm)
        )
        self.stepper_acceleration.arduino_setter.add_call(
            self.stepper.setAcceleration(self.stepper_acceleration * self.steps_per_mm)
        )

        self.target_position.arduino_setter.add_call(
            self.stepper.moveTo(self.target_position * self.steps_per_mm)
        )

        steps_in_loop = ad.add(at.Variable(name="steps_in_loop", type=uint8_t, value=0))
        ad.loop.add_call(
            steps_in_loop.set(0),
            while_(
                (steps_in_loop.increment() < self.max_steps_per_loop).and_(
                    self.stepper.run()
                )
            ),
        )

        self.basic_board_module.dataloop.prepend_call(
            self.stepper_current_position.set(
                self.stepper.currentPosition() / self.steps_per_mm.cast(float_)
            )
        )

    def post_initalization(self):
        for var in [
            self.stepper_max_speed,
            self.stepper_acceleration,
            self.target_position,
            self.stepper_current_position,
        ]:
            # var.modulvar_getter_modification(self.step_to_mm)
            # var.modulvar_setter_modification(self.mm_to_step)
            # var.data_point_modification(self.step_to_mm)
            pass

    def mm_to_step(self, mm):
        return mm * self.steps_per_mm

    def step_to_mm(self, step):
        return step / self.steps_per_mm


class AccelStepperBoard(ArduinoBoard):
    FIRMWARE = 13264008974968030663
    modules = [AccelStepperBoardModule]


if __name__ == "__main__":
    ins = AccelStepperBoard()
    ins.create_ino()
