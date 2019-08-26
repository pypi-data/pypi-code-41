import logging
import time
from ftdi_serial import Serial
from north_utils.location import Vector3
from north_utils.mixins import Runnable
from north_utils.joystick import Joystick, JoystickNotFoundError
from north_c9.controller import C9Controller, C9Error

logger = logging.getLogger(__name__)


class N9Joystick(Runnable):
    GRIPPER_AXIS = 0
    ELBOW_AXIS = 1
    SHOULDER_AXIS = 2
    COLUMN_AXIS = 3

    X_AXIS = 1
    Y_AXIS = 2
    Z_AXIS = 3

    GRIPPER_OUTPUT = 0
    PROBE_OUTPUT = 1

    def __init__(self, controller: C9Controller, velocity: int=40_000, acceleration: int=100_000,
                 moving: bool=False, ignore_missing_joystick: bool=False, z_offset: float=170.0):
        Runnable.__init__(self, logger)
        self.main_controller = controller
        self.controller = C9Controller(connection=controller.connection, use_joystick=False, ping=False, verbose=controller.verbose, read_timeout=0.2)
        self.original_speed = (velocity, acceleration)
        self.origin_bias = C9Controller.BIAS_CLOSEST
        self.velocity = velocity
        self.acceleration = acceleration
        self.deadzone = 0.01
        self.moving = moving
        self.gripper_mode = False
        self.stop_timer_end = None
        self.stop_timer_timeout = 2.0
        self.base_velocity = 10.0
        self.x_velocity_scale = 0.0
        self.y_velocity_scale = 0.0
        self.z_velocity_scale = 0.0
        self.gripper_velocity_scale = 0.0
        self.speed_scale = 1.0
        self.precise_scale = 0.05
        self.slow_speed_scale = 0.5
        self.high_speed_scale = 5.0
        self.position = [0, 0, 0, 0]
        self.z_offset = z_offset
        self.recorded_position = None
        self.gripper_spinning = False

        try:
            self.joystick = Joystick()
        except JoystickNotFoundError as err:
            if ignore_missing_joystick:
                return

            raise err

        for event, handler in self.mappings.items():
            self.joystick.add_handler(event, self.wrap_handler(handler))

        self.start()

    def start(self):
        self.joystick.start()
        Runnable.start(self)

    def stop(self):
        Runnable.stop(self)
        self.joystick.stop()

    def stop_driving(self):
        pass

    def get_current_position(self):
        elbow = self.controller.axis_position(self.ELBOW_AXIS, units=True)
        shoulder = self.controller.axis_position(self.SHOULDER_AXIS, units=True)
        gripper = self.controller.axis_position(self.GRIPPER_AXIS, units=True)
        x, y, z = self.controller.cartesian_position()
        return [x, y, z, gripper + elbow + shoulder]

    def update_current_position(self):
        self.position = self.get_current_position()

    def start_moving(self):
        self.moving = True
        self.main_controller.paused = True
        self.stop_timer_end = None
        self.recorded_position = None

        self.original_speed = self.controller.speed()
        self.origin_bias = self.controller.elbow_bias()
        self.controller.speed(self.velocity, self.acceleration)
        self.controller.elbow_bias(C9Controller.BIAS_CLOSEST)
        self.controller.home(if_needed=True)
        self.update_current_position()

    def stop_moving(self):
        self.moving = False
        self.main_controller.paused = False
        self.stop_timer_end = None
        self.controller.use_probe(False)
        self.controller.speed(*self.original_speed)
        self.controller.elbow_bias(self.origin_bias)

    def record_position(self, message: str, use_probe: bool=False) -> Vector3:
        print(message)
        self.start_moving()

        if use_probe:
            self.controller.use_probe(True)
            self.update_current_position()
        else:
            self.controller.use_probe(False)
            self.update_current_position()

        while self.recorded_position is None:
            time.sleep(0.01)

        return self.recorded_position

    def record_position_vector(self, message: str, use_probe: bool=False) -> Vector3:
        position = self.record_position(message, use_probe=use_probe)
        return Vector3(position[0], position[1], position[2])

    def record_z_offset(self, message: str='Drive the robot until the laser is focused to a point on the deck and press Record / Start', use_probe: bool=False):
        self.z_offset = self.record_z(message, offset=0, use_probe=use_probe)

    def record_z(self, message, offset=None, use_probe: bool=False):
        if offset is None:
            if self.z_offset is None:
                self.record_z_offset()

            offset = self.z_offset

        z_vector = self.record_position_vector(message, use_probe=use_probe)
        return z_vector.z() - offset

    def run(self):
        if self.moving:
            self.start_moving()

        while self.running:
            if self.stop_timer_end is not None:
                if self.moving:
                    if time.time() > self.stop_timer_end:
                        self.stop_moving()
                else:
                    self.start_moving()

            if self.moving:
                try:
                    position = [
                        self.position[0] + self.base_velocity * self.x_velocity_scale,
                        self.position[1] + self.base_velocity * self.y_velocity_scale,
                        self.position[2] + self.base_velocity * self.z_velocity_scale,
                        self.position[3] + self.base_velocity * self.gripper_velocity_scale,
                    ]

                    # normalize gripper position to -180.0 - 180.0
                    position[3] = (position[3] + 180) % 360 - 180

                    if self.x_velocity_scale != 0 or self.y_velocity_scale != 0 or self.z_velocity_scale != 0 or self.gripper_velocity_scale != 0:
                        self.controller.move_arm(*position)
                        self.position = position

                except C9Error as err:
                    if err.error_number not in (C9Error.INVALID_POSITION, C9Error.AXIS_MOVING):
                        raise err

    def wrap_handler(self, handler):
        return lambda state: handler(self, state)

    def axis_value(self, value: float) -> float:
        if abs(value) < self.deadzone:
            return 0

        return value

    def on_gripper_toggle_button(self, pressed: bool):
        if pressed:
            self.controller.output_toggle(self.GRIPPER_OUTPUT)

    def on_probe_toggle_button(self, pressed: bool):
        if pressed:
            self.controller.output_toggle(self.PROBE_OUTPUT)

    def on_elbow_swap_button(self, pressed: bool):
        if pressed:
            self.controller.swap_elbow()

    def on_spin_gripper_button(self, pressed: bool):
        if pressed:
            self.gripper_spinning = not self.gripper_spinning

    def on_gripper_mode_button(self, pressed: bool):
        self.gripper_mode = pressed

    def on_slow_speed_button(self, pressed: bool):
        if self.speed_scale == 1.0 or self.speed_scale == self.slow_speed_scale:
            self.speed_scale = self.slow_speed_scale if pressed else 1.0

    def on_high_speed_button(self, pressed: bool):
        if self.speed_scale == 1.0 or self.speed_scale == self.high_speed_scale:
            self.speed_scale = self.high_speed_scale if pressed else 1.0

    def on_stop_button(self, pressed: bool):
        if pressed:
            self.stop_timer_end = time.time() + self.stop_timer_timeout
        else:
            self.stop_timer_end = None

    def on_record_button(self, pressed: bool):
        if pressed:
            self.recorded_position = self.position

    def on_playback_mode_button(self, pressed: bool):
        pass

    def on_x_axis(self, value: float):
        self.x_velocity_scale = self.axis_value(value) * self.speed_scale * -1

    def on_y_axis(self, value: float):
        self.y_velocity_scale = self.axis_value(value) * self.speed_scale

    def on_z_axis(self, value: float):
        if not self.gripper_mode:
            self.z_velocity_scale = self.axis_value(value) * self.speed_scale * -1

    def on_gripper_left_axis(self, value: float):
        # trigger axis values range from -1 to 1, so add one to change range from 0 to 2
        self.gripper_velocity_scale = self.axis_value(value + 1) * self.speed_scale * -1

    def on_gripper_right_axis(self, value: float):
        self.gripper_velocity_scale = self.axis_value(value + 1) * self.speed_scale

    def on_x_precise_axis(self, value: float):
        self.x_velocity_scale = self.axis_value(value) * self.speed_scale * self.precise_scale * -1

    def on_y_precise_axis(self, value: float):
        self.y_velocity_scale = self.axis_value(value) * self.speed_scale * self.precise_scale * -1

    def on_gripper_precise_axis(self, value: float):
        self.gripper_velocity_scale = self.axis_value(value) * self.speed_scale * self.precise_scale

    def on_z_precise_axis(self, value: float):
        self.z_velocity_scale = self.axis_value(value) * self.speed_scale * self.precise_scale

    # mapping handlers
    def on_precise_x_axis_map(self, value: float):
        if self.gripper_mode:
            self.on_gripper_precise_axis(value)
            self.on_x_precise_axis(0.0)
        else:
            self.on_gripper_precise_axis(0.0)
            self.on_x_precise_axis(value)

    def on_precise_y_axis_map(self, value: float):
        if self.gripper_mode:
            self.on_y_precise_axis(0.0)
            self.on_z_precise_axis(value)
        else:
            self.on_y_precise_axis(value)
            self.on_z_precise_axis(0.0)

    mappings = {
        Joystick.GRIPPER_TOGGLE_BUTTON: on_gripper_toggle_button,
        Joystick.PROBE_TOGGLE_BUTTON: on_probe_toggle_button,
        Joystick.ELBOW_SWAP_BUTTON: on_elbow_swap_button,
        Joystick.SPIN_GRIPPER_BUTTON: on_spin_gripper_button,
        Joystick.STOP_BUTTON: on_stop_button,
        Joystick.RECORD_BUTTON: on_record_button,
        Joystick.SLOW_SPEED_BUTTON: on_slow_speed_button,
        Joystick.HIGH_SPEED_BUTTON: on_high_speed_button,
        Joystick.GRIPPER_MODE_BUTTON: on_gripper_mode_button,
        Joystick.PLAYBACK_MODE_BUTTON: on_playback_mode_button,

        Joystick.X_AXIS: on_x_axis,
        Joystick.Y_AXIS: on_y_axis,
        Joystick.GRIPPER_LEFT_AXIS: on_gripper_left_axis,
        Joystick.GRIPPER_RIGHT_AXIS: on_gripper_right_axis,
        Joystick.Z_AXIS: on_z_axis,
        Joystick.PRECISE_X_AXIS: on_precise_x_axis_map,
        Joystick.PRECISE_Y_AXIS: on_precise_y_axis_map
    }