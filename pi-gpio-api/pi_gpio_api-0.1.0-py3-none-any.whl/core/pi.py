from pi_gpio_api.core import pin_layout
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Warning: Not using a Raspberry Pi board')
    import pi_gpio_api.core.GPIO_mock as GPIO


class Pi(object):
    channel_functions = {
        GPIO.IN: 'Input',
        GPIO.OUT: 'Output',
        GPIO.I2C: 'I2C',
        GPIO.SPI: 'SPI',
        GPIO.HARD_PWM: 'HARD_PWM',
        GPIO.SERIAL: 'Serial',
        GPIO.UNKNOWN: 'Unknown'
    }

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.status = {}

    def __del__(self):
        self.clean()

    def clean(self, channel=None):
        if channel:
            return GPIO.cleanup(channel)
        GPIO.cleanup()

    def __get_function_by_string(self, fcn_string):
        """
        Looks the channel_functions dict by key
        :param fcn_string: string with the value to lookup
        :return: GPIO library object for the given function
        """
        for k, v in self.channel_functions.items():
            if v.lower() == fcn_string.lower():
                return k

    def set_channel_function(self, channel, fnc):
        """
        Sets up a specific channel as input or output
        :param channel: int with the number of the pin to setup
        :param fnc: string, either 'input' or 'output'
        :return: Nothing
        """
        if channel not in pin_layout.IO_PINS:
            raise AttributeError('Can\'t change function to non IO pins')

        self.clean(channel)
        try:
            GPIO.setup(channel, self.__get_function_by_string(fnc))
        except Exception:
            raise Exception('Can\'t use channel {} as "{}" on this board'.
                            format(channel, fnc))

    def read(self, channel):
        """
        Reads the status of a given channel
        :param channel: int, channel to read
        :return: value/measure of the given channel
        """
        return GPIO.input(channel)

    def write(self, channel, state):
        """
        Writes a value into a given pin
        :param channel: int, channel to change state
        :param state: boolean, value to write into a pin
        :return: Nothing
        """
        if channel not in pin_layout.IO_PINS:
            raise AttributeError('Can\'t write to non IO pins')

        state = GPIO.HIGH if state else GPIO.LOW
        try:
            GPIO.output(channel, state)
        except Exception:
            raise Exception('Couldn\'t write value to the channel {}'.
                            format(channel))

    def info(self):
        """
        Returns data specific to the board where the software is running
        :return: dict with board information
        """
        return GPIO.RPI_INFO,

    def gpio_status(self, channel=None):
        """
        Creates a dict of data for a given channel/set of channels
        :param channel: int or list of integers with the channels to fetch
        data from. If the parameter is not given, returns the status of all
        channels
        :return: dict of data abour one/a list of channels
        """
        pins = pin_layout.ALL_PINS if not channel else channel
        if not (isinstance(pins, list) or isinstance(pins, tuple)):
            pins = [pins]

        data = []
        for p in pins:
            status = {}
            status['pin'] = p
            status['pin_function'] = self.__pin_function_name(p)
            try:
                if p in pin_layout.IO_PINS:
                    status['pin_state'] = self.read(p)
            except Exception:
                continue
            data.append(status)

        return data

    def __pin_function_name(self, pin):
        """
        Returns the description/use of a given channel
        :param pin: int, with the number of the pin to lookup
        :return: string with the description of the pin
        """
        try:
            return self.channel_functions[GPIO.gpio_function(pin)]
        except Exception:
            return pin_layout.pin_description(pin)
