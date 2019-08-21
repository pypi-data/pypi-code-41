import time
import warnings


def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif upper is not None and value > upper:
        return upper
    elif lower is not None and value < lower:
        return lower
    return value


try:
    # get monotonic time to ensure that time deltas are always positive
    _current_time = time.monotonic
except AttributeError:
    # time.monotonic() not available (using python < 3.3), fallback to time.time()
    _current_time = time.time
    warnings.warn('time.monotonic() not available in python < 3.3, using time.time() as fallback')


class PID(object):
    """
    PID controller of Mixlinker
    """

    def __init__(self, kp=1.0, ki=0.0, kd=0.0,
                 set_pressure=0.5,
                 thresholds=(-10, 10),
                 throttle_limits=((30, 60), (40, 65), (50, 70)),
                 output_limits=(None, None),
                 auto_mode=True):
        """
        :param kp: The value for the proportional gain kp
        :param ki: The value for the integral gain ki
        :param kd: The value for the derivative gain kd
        :param set_pressure: The initial set_pressure that the PID will try to achieve
        :param thresholds: the output threshold to decide whether to change
        :param throttle_limits: the limits of throttle on every gear of burner
        :param output_limits: The initial output limits to use, given as an iterable with 2 elements, for example:
                              (lower, upper). The output will never go below the lower limit or above the upper limit.
                              Either of the limits can also be set to None to have no limit in that direction. Setting
                              output limits also avoids integral windup, since the integral term will never be allowed
                              to grow outside of the limits.
        :param auto_mode: Whether the controller should be enabled (in auto mode) or not (in manual mode)
        """
        self.kp, self.ki, self.kd = kp, ki, kd
        self.set_pressure = set_pressure
        self.lower_threshold, self.upper_threshold = thresholds
        self.throttle_limits = throttle_limits
        self._min_output, self._max_output = output_limits
        self._auto_mode = auto_mode

        self._proportional = 0
        self._integral = 0
        self._derivative = 0
        self._last_time = _current_time()
        self._last_pressure = None

    def __call__(self, input_pressure, input_gear, input_angle):
        """
        Call the PID controller with *input_gear*, *input_pressure*, *input_angle*
        and calculate and return a control output.
        """
        if not self.auto_mode:
            return input_gear, input_angle

        now = _current_time()
        dt = now - self._last_time if now - self._last_time else 1e-3

        # compute error terms
        error = self.set_pressure - input_pressure

        d_input = input_pressure - (self._last_pressure if self._last_pressure is not None else input_pressure)

        # compute the proportional term
        self._proportional = self.kp * error

        # compute integral and derivative terms
        self._integral += self.ki * error * dt
        self._integral = _clamp(self._integral, self.output_limits)  # avoid integral windup

        self._derivative = -self.kd * d_input / dt

        # compute final output
        output = self._proportional + self._integral + self._derivative
        output = _clamp(output, self.output_limits)

        # keep track of state
        self._last_pressure = input_pressure
        self._last_time = now

        # decision conditions
        if output > self.upper_threshold:
            if input_angle - 5 < self.throttle_limits[input_gear - 1][0]:
                output_gear = input_gear + 1
                output_angle = input_angle
            else:
                output_angle = input_angle - 5
                output_gear = input_gear
        elif output < self.lower_threshold:
            if input_angle + 5 > self.throttle_limits[input_gear - 1][1]:
                output_gear = input_gear - 1
                output_angle = input_angle
            else:
                output_angle = input_angle + 5
                output_gear = input_gear
        else:
            output_gear = input_gear
            output_angle = input_angle
        return output_gear, output_angle

    @property
    def components(self):
        """
        The P-, I- and D-terms from the last computation as separate components as a tuple. Useful for visualizing
        what the controller is doing or when tuning hard-to-tune systems.
        """
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        """The tunings used by the controller as a tuple: (kp, ki, kd)"""
        return self.kp, self.ki, self.kd

    @tunings.setter
    def tunings(self, tunings):
        """Setter for the PID tunings"""
        self.kp, self.ki, self.kd = tunings

    @property
    def auto_mode(self):
        """Whether the controller is currently enabled (in auto mode) or not"""
        return self._auto_mode

    @auto_mode.setter
    def auto_mode(self, enabled):
        """Enable or disable the PID controller"""
        self.set_auto_mode(enabled)

    def set_auto_mode(self, enabled, input_pressure=None):
        """
        Enable or disable the PID controller, optionally setting the last output value.
        This is useful if some system has been manually controlled and if the PID should take over.
        In that case, pass the last output variable (the control variable) and it will be set as the starting
        I-term when the PID is set to auto mode.
        :param enabled: Whether auto mode should be enabled, True or False
        :param input_pressure: The last output, or the control variable, that the PID should start from
                            when going from manual mode to auto mode
        """
        if enabled and not self._auto_mode:
            # switching from manual mode to auto, reset
            self._last_pressure = input_pressure
            self._last_time = _current_time()
            self._proportional = 0
            self._integral = (input_pressure if input_pressure is not None else 0)
            self._integral = _clamp(self._integral, self.output_limits)

        self._auto_mode = enabled

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper). See also the *output_limts* parameter in
        :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """Setter for the output limits"""
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if None not in limits and max_output < min_output:
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output

        self._integral = _clamp(self._integral, self.output_limits)
        self._last_pressure = _clamp(self._last_pressure, self.output_limits)
