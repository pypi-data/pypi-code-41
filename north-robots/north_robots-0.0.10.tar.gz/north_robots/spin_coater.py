from typing import Optional, List, Tuple
import time
import threading
import atexit
from north_c9.controller import C9Controller
from north_c9.axis import RevoluteAxis, Output
from north_robots.robot import Robot, RobotError


class SpinCoaterError(RobotError):
    pass


class SpinCoaterProfileRunningError(SpinCoaterError):
    pass


class SpinCoater(Robot):
    def __init__(self, controller: C9Controller, axis: int=0, lid_output: int=0, suction_output: int=1, home: bool=False):
        Robot.__init__(self, controller)
        self.axis = RevoluteAxis(controller, axis)
        self.cover = Output(controller, lid_output)
        self.suction = Output(controller, suction_output)
        self.spin_profile_thread: Optional[threading.Thread] = None
        self.spin_profile_running: bool = False

        if home:
            self.home()

        atexit.register(self.halt)

    @property
    def spinning(self):
        return self.controller.axis_moving(self.axis.axis_number)

    def halt(self, timeout: float=5.0):
        self.spin_profile_running = False

        if self.spin_profile_thread:
            self.spin_profile_thread.join(timeout)

        if self.axis.moving():
            self.axis.spin_stop(wait=False)

    def home(self):
        self.axis.home()

    def open_cover(self):
        self.cover.on()

    def close_cover(self):
        self.cover.off()

    def suction_on(self):
        self.suction.on()

    def suction_off(self):
        self.suction.off()

    def spin(self, velocity_rpm: float, acceleration_rpm: float, duration: Optional[float]=None):
        self.axis.spin(velocity_rpm, acceleration_rpm, duration)

    def wait_for_stop(self):
        if self.spin_profile_running:
            self.spin_profile_thread.join()
        else:
            self.axis.wait()

    def spin_stop(self, profile_timeout: float=5.0, wait: bool=True, stop_thread: bool=True):
        self.axis.spin_stop(wait=False)

        if stop_thread and self.spin_profile_thread is not None and self.spin_profile_running:
            self.spin_profile_running = False

            if wait:
                self.spin_profile_thread.join(timeout=profile_timeout)

        if wait:
            self.axis.wait()

    def run_spin_profile(self, profile: List[Tuple[int, int, float]], home: bool=False):
        self.spin_profile_running = True

        try:
            for velocity, acceleration, duration in profile:
                self.spin(velocity, acceleration)

                end_time = time.time() + duration
                while time.time() < end_time:
                    if not self.spin_profile_running:
                        return self.halt()

                    time.sleep(0.01)
        except KeyboardInterrupt:
            return self.halt()

        self.spin_stop(wait=True, stop_thread=False)

        time.sleep(1)

        if home:
            self.axis.home()

        self.spin_profile_running = False

    def spin_profile(self, profile: List[Tuple[int, int, float]], wait: bool=True, home: bool=False):
        if wait:
            self.run_spin_profile(profile, home=home)
        else:
            if self.spin_profile_running:
                raise SpinCoaterProfileRunningError(f'Cannot run profile while a profile is currently running')

            self.spin_profile_thread = threading.Thread(target=self.run_spin_profile, args=[profile], daemon=True)
            self.spin_profile_thread.start()
