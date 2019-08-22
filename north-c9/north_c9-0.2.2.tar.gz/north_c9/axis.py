from typing import Optional
import time
from north_utils.motion import degrees_to_counts, counts_to_degrees, mm_to_counts, counts_to_mm, cps_to_rpm, rpm_to_cps
from north_c9.controller import C9Controller


class AxisError(Exception):
    pass


class AxisMoveError(AxisError):
    pass


class JointError(Exception):
    pass


class RevoluteJointError(JointError):
    pass


class PrismaticJointError(JointError):
    pass


class Output:
    def __init__(self, controller: C9Controller, output_number: int):
        self.controller = controller
        self.output_number = output_number

    @property
    def state(self):
        return self.controller.output(self.output_number)

    def set_state(self, state):
        self.controller.output(self.output_number, state)

    def on(self):
        self.set_state(True)

    def off(self):
        self.set_state(False)

    def toggle(self):
        self.set_state(not self.state)


class OpenOutput(Output):
    def __init__(self, controller: C9Controller, output_number: int, open_state: bool=True):
        Output.__init__(self, controller, output_number)
        self.open_state = open_state

    def open(self, open_state: bool=True):
        state = self.open_state if open_state else not self.open_state
        self.set_state(state)

    def close(self):
        self.set_state(not self.open_state)


class Axis:
    def __init__(self,
                 controller: C9Controller,
                 axis_number: int,
                 velocity_counts: Optional[int]=None,
                 acceleration_counts: Optional[int]=None,
                 max_position: Optional[int]=None,
                 max_current: Optional[int]=None,
                 home_velocity_counts: Optional[int]=None,
                 home_acceleration_counts: Optional[int]=None,
                 home_max_current: Optional[int]=None,
                 home_to_block: bool=True,
                 main: bool=False,
                 reversed: bool=False,
                 **kwargs) -> None:
        self.controller = controller
        self.axis_number = axis_number
        self.velocity = velocity_counts
        self.acceleration = acceleration_counts
        self.max_current = max_current
        self.max_position = max_position
        self.reversed = reversed
        self.sign = -1 if reversed else 1
        self.main = main
        self.home_velocity = home_velocity_counts if home_velocity_counts is not None else velocity_counts or 0 / 2
        self.home_acceleration = home_acceleration_counts if home_acceleration_counts is not None else velocity_counts or 0 / 2
        self.home_max_current = home_max_current
        self.home_to_block = home_to_block and self.max_position is not None

        self.write_axis_settings()

    @property
    def position(self):
        return self.controller.axis_position(self.axis_number)

    @property
    def current_velocity(self):
        return self.controller.axis_velocity(self.axis_number)

    def write_axis_settings(self):
        if self.max_current is not None:
            self.set_max_current(self.max_current)

    def set_max_current(self, current, update: bool=True):
        self.controller.axis_current(self.axis_number, current, max=True)
        if update:
            self.max_current = current

    def home(self):
        if self.main:
            raise AxisError('Only aux axis can be homed manually')

        if self.home_max_current is not None:
            self.set_max_current(self.home_max_current)

        if self.home_to_block:
            self.move(-self.max_position * self.sign, velocity=self.home_velocity, acceleration=self.home_acceleration, relative=True, wait=True)

        self.controller.home(self.axis_number)

        if self.home_max_current is not None:
            self.set_max_current(self.max_current)

    def moving(self):
        return self.controller.axis_moving(self.axis_number)

    def wait(self):
        return self.controller.wait_for_axis(self.axis_number)

    def move(self, counts: int, velocity: Optional[int]=None, acceleration: Optional[int]=None, relative: bool=False,
             wait: bool=True):
        if velocity is None:
            velocity = self.velocity

        if acceleration is None:
            acceleration = self.acceleration

        if velocity is None and acceleration is None:
            raise AxisMoveError('Error moving joint, no velocity or acceleration given (and no defaults set for joint)')

        self.controller.move_axis(self.axis_number, counts, velocity, acceleration, wait=wait, units=self.main, relative=relative)


class RevoluteAxis(Axis):
    def __init__(self,
                 controller: C9Controller,
                 axis: int,
                 counts_per_revolution: float=360.0,
                 zero_position_degrees: float=0.0,
                 position_degrees: float=0,
                 velocity_degrees: float=None,
                 acceleration_degrees: float=None,
                 inverted: bool=False,
                 **kwargs) -> None:
        kwargs['position'] = kwargs.get('position', degrees_to_counts(position_degrees, counts_per_revolution))
        kwargs['velocity'] = kwargs.get('velocity', degrees_to_counts(velocity_degrees, counts_per_revolution))
        kwargs['acceleration'] = kwargs.get('acceleration', degrees_to_counts(acceleration_degrees, counts_per_revolution))
        Axis.__init__(self, controller, axis, inverted=inverted, **kwargs)

        self.zero_position_degrees = zero_position_degrees
        self.counts_per_revolution = counts_per_revolution
        self.angle_sign = -1 if inverted else 1

    @property
    def position_degrees(self) -> float:
        return counts_to_degrees(self.position, self.counts_per_revolution, sign=self.angle_sign) - self.zero_position_degrees

    @property
    def velocity_degrees(self) -> float:
        return counts_to_degrees(self.velocity, self.counts_per_revolution) or 0

    @property
    def current_velocity_degrees(self) -> float:
        return counts_to_degrees(self.current_velocity, self.counts_per_revolution) or 0

    @property
    def current_velocity_rpm(self) -> float:
        return cps_to_rpm(self.current_velocity, self.counts_per_revolution) or 0

    @velocity_degrees.setter
    def velocity_degrees(self, velocity: float):
        self.velocity = degrees_to_counts(velocity, self.counts_per_revolution) or 0

    @property
    def acceleration_degrees(self) -> float:
        return counts_to_degrees(self.acceleration, self.counts_per_revolution) or 0

    @acceleration_degrees.setter
    def acceleration_degrees(self, acceleration: float):
        self.acceleration = degrees_to_counts(acceleration, self.counts_per_revolution)

    def move_degrees(self, degrees: float, velocity_degrees: Optional[float]=None,
                     acceleration_degrees: Optional[float]=None, relative: bool=False, wait: bool=True):

        if not relative:
            degrees += self.zero_position_degrees

        counts = degrees_to_counts(degrees * self.angle_sign, self.counts_per_revolution) or 0
        velocity = degrees_to_counts(velocity_degrees, self.counts_per_revolution)
        acceleration = degrees_to_counts(acceleration_degrees, self.counts_per_revolution)

        self.move(counts, velocity, acceleration, relative=relative, wait=wait)

    def spin(self, velocity_rpm: float, acceleration_rpm: float, duration: Optional[float]=None):
        velocity_counts = rpm_to_cps(velocity_rpm, self.counts_per_revolution)
        acceleration_counts = rpm_to_cps(acceleration_rpm, self.counts_per_revolution)

        self.controller.spin_axis(self.axis_number, velocity=velocity_counts, acceleration=acceleration_counts)

        if duration is not None:
            time.sleep(duration)
            self.spin_stop()

    def spin_stop(self, wait: bool=False):
        self.controller.spin_axis(self.axis_number, stop=True)

        if wait:
            self.controller.wait_for_axis(self.axis_number)


class PrismaticAxis(Axis):
    def __init__(self,
                 controller: C9Controller,
                 axis: int,
                 counts_per_mm: float=1.0,
                 position_mm: float=0.0,
                 zero_position_mm: float=0.0,
                 velocity_mm: Optional[float]=None,
                 acceleration_mm: Optional[float]=None,
                 inverted: bool=False,
                 **kwargs) -> None:
        kwargs['position'] = kwargs.get('position', mm_to_counts(position_mm, counts_per_mm))
        kwargs['velocity'] = kwargs.get('velocity', mm_to_counts(velocity_mm, counts_per_mm))
        kwargs['acceleration'] = kwargs.get('acceleration', mm_to_counts(acceleration_mm, counts_per_mm))
        Axis.__init__(self, controller, axis, **kwargs)

        self.counts_per_mm = counts_per_mm
        self.zero_position_mm = zero_position_mm
        self.sign = -1 if inverted else 1

    @property
    def position_mm(self) -> float:
        return counts_to_mm(self.position, self.counts_per_mm) * self.sign + self.zero_position_mm

    @property
    def velocity_mm(self) -> float:
        return counts_to_mm(self.velocity, self.counts_per_mm) or 0

    @velocity_mm.setter
    def velocity_mm(self, velocity: float):
        self.velocity = mm_to_counts(velocity, self.counts_per_mm) or 0

    @property
    def acceleration_mm(self) -> float:
        return counts_to_mm(self.acceleration, self.counts_per_mm) or 0

    @acceleration_mm.setter
    def acceleration_mm(self, acceleration: float):
        self.acceleration = mm_to_counts(acceleration, self.counts_per_mm) or 0

    def move_mm(self, mm: float, velocity_mm: Optional[float]=None, acceleration_mm: Optional[float]=None,
                relative: bool=False, wait: bool=True):
        if not relative:
            mm -= self.zero_position_mm

        counts = mm_to_counts(mm * self.sign, self.counts_per_mm) or 0
        velocity = mm_to_counts(velocity_mm, self.counts_per_mm)
        acceleration = mm_to_counts(acceleration_mm, self.counts_per_mm)

        self.move(counts, velocity, acceleration, relative=relative, wait=wait)
