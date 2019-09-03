"""Servo class."""
import json
from websocket import create_connection
import asyncio
import multiprocessing as mp
from threading import Thread
from tkinter import TclError
from ADwin import ADwinError
from math import pow, copysign
from time import sleep, time
import jsonpickle
import numpy as np
from openqlab.analysis.servo_design import ServoDesign
from pandas import DataFrame
from matplotlib import pyplot as plt
from nqontrol import settings, general
import logging as log
from nqontrol.errors import *


def _convertVolt2Int(value, mode=0, unsigned=False):
    if type(value) is list:
        value = np.array(value)
    result = 0.1 * value * 0x8000 * pow(2, mode)

    upper_limit = 0x7fff
    lower_limit = -0x8000
    if type(result) in (float, np.float64, np.float32):
        result = int(round(result, 0))
        if result > upper_limit:
            result = upper_limit
        if result < lower_limit:
            result = lower_limit
    elif isinstance(result, np.ndarray):
        result = result.astype(int)
        result[result > upper_limit] = upper_limit
        result[result < lower_limit] = lower_limit
    else:
        raise TypeError('The type {} is not supported.'.format(type(value)))

    if unsigned:
        result += 32768
    return result


def _convertInt2Volt(value, mode=0):
    if type(value) is list:
        value = np.array(value)
    return 10.0 * (value / 0x8000 - 1) / pow(2, mode)


def _rearrange_filter_coeffs(filter):
    b = filter[0:3]
    a = filter[3:6]
    return [b[0], a[1], a[2], b[1] / b[0], b[2] / b[0]]


def _convertStepsize2Frequency(stepsize):
    if stepsize is None:
        return None
    return stepsize * settings.SAMPLING_RATE / settings.RAMP_DATA_POINTS


def _convertFrequency2Stepsize(frequency):
    # period_time = RAMP_DATA_POINTS/stepsize / SAMPLING_RATE
    # f = stepsize * SAMPLING_RATE / RAMP_DATA_POINTS
    # stepsize = f / SAMPLING_RATE * RAMP_DATA_POINTS
    if frequency is None:
        return None
    stepsize = int(frequency * settings.RAMP_DATA_POINTS / settings.SAMPLING_RATE)
    if stepsize < 1:
        stepsize = 1
        log.warning('The frequency is too low, using the lowest possible.')
    elif stepsize > 255:
        stepsize = 255
        log.warning('The frequency is too high, using the highest possible.')

    frequency = _convertStepsize2Frequency(stepsize)
    log.info('frequency: {:.2f} Hz'.format(frequency))

    return stepsize


class Servo:
    """
    Servo object that communicates with a control channel of the ADwin.

    `readFromFile` overwrites all other parameters.

    Parameters
    ----------
    channel: :obj:`int`
        Channel used vor the Servo.
        Possible is `1..8`
        Channel number is used for input,
        output and process number
    adw: :obj:`ADwin`
        For all servos of a :obj:`ServoDevice` to use the same :obj:`ADwin` object,
        it is necessary to pass an ADwin object.
    applySettings: :obj:`str` or `dict`
        Apply settings directly from file or dict.
    offset: :obj:`offset`
        Overall offset.
    gain: :obj:`float`

    filters: 5 * 5 :obj:`list`
        Filter coefficient matrix. Default is a 0.0 matrix.
    name: :obj:`str`
        Choose an optional name for this servo.
    """

    DONT_SERIALIZE = ['_adw', '_subProcess', '_fifoBuffer', '_tempFeedback']
    JSONPICKLE = ['servoDesign']
    MIN_REFRESH_TIME = .02
    DEFAULT_FILTERS = [
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0]
    ]
    DEFAULT_COLUMNS = ['input', 'aux', 'output']
    _manager = mp.Manager()
    realtime = _manager.dict({
        'enabled': False,
        'ydata': DEFAULT_COLUMNS,
        'ylim': None,
        'refreshTime': 0.1,
    })
    DEFAULT_FIFO_STEPSIZE = 10
    """
    Control realtime plotting.

    .. code:: python

        realtime = {
            'enabled': False,
            'ydata': ['input', 'aux', 'output'],
            'ylim': None,
            'refreshTime': 0.1,
        }
    """

    # TODO ramp speed
    ########################################
    # Predefined methods
    ########################################
    def __init__(self,
                 channel,
                 adw,
                 applySettings=None,
                 offset=0.0,
                 gain=1.0,
                 filters=None,
                 name=None):
        """
        Create the servo object, also on ADwin.

        `readFromFile` overwrites all other parameters.

        Parameters
        ----------
        deviceNumber: Number of the ADwin-Pro device.
        channel:      Channel used for the Servo.
                      Possible is `1..8`
                      Channel number is used for input,
                      output and process number
        offset=0.0:   Overall offset
        filters:      Filter coefficient matrix. Default is a 0.0 matrix.
        """
        MAX_CHANNELS = 8

        if 1 > channel > MAX_CHANNELS:
            raise ValueError('There are max 8 channels.')
        self._channel = channel
        if name is None:
            self.name = 'Servo ' + str(channel)
        else:
            self.name = name
        if filters is None:
            filters = self.DEFAULT_FILTERS

        # State dictionaries
        self._state = self._manager.dict({
            # Control parameters
            'offset': offset,
            'gain': gain,
            'filters': filters,
            'inputSensitivity': 0,
            'auxSensitivity': 0,
            # Control flags
            'filtersEnabled': [False] * 5,
            'auxSw': False,
            'offsetSw': False,
            'outputSw': False,
            'inputSw': False,
            # 'snapSw': False,
        })
        # self._snap = self._manager.dict({
        #     'limit': 0,
        #     'greater': True,
        # })
        self._ramp = self._manager.dict({
            'amplitude': .1,
            'minimum': 0,
            'stepsize': 20,
        })
        self._autolock = self._manager.dict({
            'state': 0,
            'threshold': 0,
            'min': -5,
            'max': 5,
            'greater': True,
            'relock': False,
        })
        self._fifo = self._manager.dict({
            'stepsize': self.DEFAULT_FIFO_STEPSIZE,
            'maxlen': settings.FIFO_MAXLEN,
        })
        if self._fifo['maxlen'] * 2 > settings.FIFO_BUFFER_SIZE:
            raise ConfigurationError("FIFO_BUFFER_SIZE must be at least twice as big as _fifo['maxlen'].")
        self._fifoBuffer = None
        self._subProcess = None

        # has to be initalized as None / could maybe include in the loading?
        self._tempFeedback = None
        self._tempFeedbackSettings = self._manager.dict({
            'dT': None,
            'mtd': None,
            'update_interval': 1,
            'voltage_limit': 5,
        })

        # ServoDesign object
        self.servoDesign: ServoDesign = ServoDesign()

        # Use adwin object
        self._adw = adw

        try:
            if applySettings:
                # loadSettings calls `_sendAllToAdwin()`
                self.loadSettings(applySettings)
            else:
                self._sendAllToAdwin()
        except ADwinError as e:
            print(e, "Servo " + str(self._channel) + ": Couldn't write to ADwin.")

    def __str__(self):
        """Name of the object."""
        print("Name: " + self.name +
              ", channel: " + str(self._channel))

    ########################################
    # Help methods
    ########################################
    def _sendAllToAdwin(self):
        """Write all settings to ADwin."""
        # Control parameters
        self.offset = self._state['offset']
        self.gain = self._state['gain']
        self.filters = self._state['filters']
        self.inputSensitivity = self._state['inputSensitivity']
        self.auxSensitivity = self._state['auxSensitivity']

        # Control flags
        self._sendFilterControl()
        self.auxSw = self._state['auxSw']
        self.offsetSw = self._state['offsetSw']
        self.outputSw = self._state['outputSw']
        self.inputSw = self._state['inputSw']

    def _triggerReload(self):
        """Trigger bit to trigger reloading of parameters."""
        par = self._adw.Get_Par(settings.PAR_RELOADBIT)
        # only trigger if untriggered
        if not general.readBit(par, self._channel - 1):
            par = general.changeBit(par, self._channel - 1, True)
            self._adw.Set_Par(settings.PAR_RELOADBIT, par)
        else:
            raise Exception("ADwin has been triggered to reload the shared RAM within 10µs or the realtime program doesn't run properly.")

    def _readFilterControl(self):
        c = self._adw.Get_Par(settings.PAR_FCR + self._channel)
        # read control bits
        self._state['auxSw'] = general.readBit(c, 9)
        for i in list(range(5)):
            self._state['filtersEnabled'][i] = general.readBit(c, 4 + i)
        # self._state['snapSw'] = general.readBit(c, 3)
        self._state['offsetSw'] = general.readBit(c, 2)
        self._state['outputSw'] = general.readBit(c, 1)
        self._state['inputSw'] = general.readBit(c, 0)

    def _readLockControl(self):
        indexoffset = (self._channel - 1) * 5

        state = self._adw.GetData_Long(settings.DATA_LOCK, 1 + indexoffset, 1)[0]
        if state in range(8):
            self._autolock['state'] = (state & 0x3)
            self._autolock['relock'] = general.readBit(state, 2)

    def _sendFilterControl(self):
        # read current state
        c = self._adw.Get_Par(settings.PAR_FCR + self._channel)

        # set control bits
        c = general.changeBit(c, 9, self._state['auxSw'])
        for i in list(range(5)):
            c = general.changeBit(c, 4 + i, self._state['filtersEnabled'][i])
        # c = general.changeBit(c, 3, self._state['snapSw'])
        c = general.changeBit(c, 2, self._state['offsetSw'])
        c = general.changeBit(c, 1, self._state['outputSw'])
        c = general.changeBit(c, 0, self._state['inputSw'])

        self._adw.Set_Par(settings.PAR_FCR + self._channel, c)

    @property
    def channel(self):
        return self._channel

    ########################################
    # Change servo state
    ########################################
    def setRamp(self, frequency=None, amplitude=None, enableFifo=True):
        """Deprecated version of :obj:`nqontrol.Servo.enableRamp`."""
        log.warning('DEPRECATION: Use the new enableRamp().')
        self.enableRamp(frequency, amplitude, enableFifo)

    def enableRamp(self, frequency=None, amplitude=None, enableFifo=True):
        """
        Enable the ramp on this servo.

        Parameters
        ----------
        frequency: :obj:`float` in Hz.
            The frequency will be translated to a step size which is a 1 byte value.
            Therefore it is a rather discrete value with a low possible range.
        amplitude: :obj:`float` from 0 to 10
            ramp amplitude in volt.
        enableFifo: :obj:`bool`
            Defaults to :obj:`True`.
            Possible not to enable the FIFO buffering for this servo.
        """
        if self._autolock['state']:
            raise UserInputError('Autolock is active, ramp cannot be activated on this channel.')

        if frequency is None:
            stepsize = self._ramp['stepsize']
        else:
            stepsize = _convertFrequency2Stepsize(frequency)
            self._ramp['stepsize'] = stepsize

        if amplitude is None:
            amplitude = self._ramp['amplitude']
        else:
            self._ramp['amplitude'] = amplitude

        if not (0 <= amplitude <= 10):
            raise ValueError('The amplitude must be between 0 and 10!')

        self._ramp['minimum'] = 0

        control = stepsize * 0x100
        control += self._channel
        self._adw.Set_Par(settings.PAR_RCR, control)
        self._adw.Set_FPar(settings.FPAR_RAMPAMP, amplitude / 10)

        if enableFifo:
            factor = 1.2
            fifoStepsize = int(factor * settings.RAMP_DATA_POINTS / self._fifo['maxlen'] / stepsize)
            if fifoStepsize == 0:
                fifoStepsize = 1
            self.enableFifo(fifoStepsize)
            assert(self.fifoStepsize == fifoStepsize)

    def stopRamp(self):
        """Deprecated version of :obj:`nqontrol.Servo.disableRamp`."""
        log.warning('DEPRECATION: Use the new disableRamp().')
        self.disableRamp()

    def disableRamp(self):
        """Stop the ramp."""
        self._ramp['minimum'] = 0
        self._adw.Set_Par(settings.PAR_RCR, 0)

    @property
    def filterStates(self):
        """
        List of all filter states.

        :getter: Return the filter states.
        :setter: Set all filter states.
        :type: :obj:`list` of :code:`5*`:obj:`bool`.
        """
        self._readFilterControl()
        return self._state['filtersEnabled']

    @filterStates.setter
    def filterStates(self, filtersEnabled):
        self._state['filtersEnabled'] = filtersEnabled
        self._sendFilterControl()

    def filterState(self, id, enabled):
        """Enable or disable the SOS filter with number `id`.

        Parameters
        ----------
        id: :obj:`int` index from 0 to 4
            Index of the filter to control.
        enabled: :obj:`bool`
            :obj:`True` to enable.
        """
        filtersEnabled = self._state['filtersEnabled']
        filtersEnabled[id] = enabled
        self._state['filtersEnabled'] = filtersEnabled
        self._sendFilterControl()

    @property
    def auxSw(self):
        """
        Switch for mixing the aux signal to the output.

        :getter: Return the state of aux mixing.
        :setter: Enable or disable the aux mixing.
        :type: :obj:`bool`
        """
        self._readFilterControl()
        return self._state['auxSw']

    @auxSw.setter
    def auxSw(self, enabled):
        self._state['auxSw'] = enabled
        self._sendFilterControl()

    @property
    def rampEnabled(self):
        control = self._adw.Get_Par(settings.PAR_RCR)
        if control & 15 == self._channel:
            return True
        else:
            return False

    @property
    def rampAmplitude(self):
        """
        Amplitude of servo ramp.

        :getter: Return amplitude of ramp channel.
        :setter: Set the amplitude of ramp channel.
        :type: :obj:`int`
        """
        return self._ramp['amplitude']

    @rampAmplitude.setter
    def rampAmplitude(self, amplitude):
        if not (0 <= amplitude <= 10):
            raise UserInputError('The amplitude must be between 0 and 10!')
        self._ramp['amplitude'] = amplitude
        if self.rampEnabled:
            self.enableRamp()

    @property
    def rampFrequencyMax(self):
        """Maximum frequency that is possible for a ramp at the current sampling frequency."""
        return _convertStepsize2Frequency(255)

    @property
    def rampFrequencyMin(self):
        """Minimum frequency that is possible for a ramp at the current sampling frequency."""
        return _convertStepsize2Frequency(1)

    @property
    def rampFrequency(self):
        """
        Step size of servo ramp.

        :getter: Return step size of ramp channel.
        :setter: Set the step size of ramp channel.
        :type: :obj:`int`
        """
        return _convertStepsize2Frequency(self._ramp['stepsize'])

    @rampFrequency.setter
    def rampFrequency(self, frequency):
        self._ramp['stepsize'] = _convertFrequency2Stepsize(frequency)
        if self.rampEnabled:
            self.enableRamp()

    @property
    def offsetSw(self):
        """
        Enable or disable offset switch.

        :getter: Return the state of the switch.
        :setter: Enable or disable the offset.
        :type: :obj:`bool`
        """
        self._readFilterControl()
        return self._state['offsetSw']

    @offsetSw.setter
    def offsetSw(self, enabled):
        self._state['offsetSw'] = enabled
        self._sendFilterControl()

    def offsetAutoSet(self):
        """
        Automatically adjust the input offset.

        Before using it ensure to block the beam.
        It takes the mean value of {} data points.
        After changing the input amplification it may be necessary to adjust the offset.
        """.format(10 * settings.FIFO_MAXLEN)
        self.enableFifo(1)
        n = 10000
        self._waitForBufferFilling(n)
        df = self._readoutNewData(n=n)

        self.offset = - df['input'].mean()

    @property
    def lockState(self):
        """Return the lock state.

        '0': off
        `1`: search
        `2`: lock

        Returns
        -------
        :obj:`int`
            The lock state.

        """
        self._readLockControl()
        return self._autolock['state']

    @property
    def lockThreshold(self):
        """Get or set the autolock threshold.

        :getter: Return the threshold.
        :setter: Set the threshold.
        :type: :obj:`float`
        """
        return self._autolock['threshold']

    @lockThreshold.setter
    def lockThreshold(self, threshold):
        try:
            float(threshold)
        except ValueError:
            raise TypeError('threshold must be a float or int.')
        index_offset = (self._channel - 1) * 5  # the lock state parameter is set on index 1, 6, 12 etc., as each servo channel occupies 5 indices (as of current version)
        self._autolock['threshold'] = threshold
        threshold = _convertVolt2Int(threshold, self.auxSensitivity, True)
        threshold = general.changeBit(threshold, 16, self.lockGreater)
        # Sending values to ADwin
        self._adw.SetData_Long([threshold], settings.DATA_LOCK, 2 + index_offset, 1)

    @property
    def lockSearchMin(self):
        """Get or set the autolock search range minimum.

        :getter: Return the threshold.
        :setter: Set the threshold.
        :type: :obj:`float`
        """
        return self._autolock['min']

    @lockSearchMin.setter
    def lockSearchMin(self, value):
        try:
            float(value)
        except ValueError:
            raise TypeError('value must be a float or int.')
        if not -10 <= value <= 10:
            raise ValueError('Search minimum has to be between -10 and 10 volts.')
        if value > self._autolock['max']:
            raise ValueError('Please make sure the maximum is greater than the minimum or try setting the maximum first.')
        index_offset = (self._channel - 1) * 5  # the lock state parameter is set on index 1, 6, 12 etc., as each servo channel occupies 5 indices (as of current version)
        self._autolock['min'] = value
        min = _convertVolt2Int(value, self.auxSensitivity, True)
        # Sending values to ADwin
        self._adw.SetData_Long([min], settings.DATA_LOCK, 3 + index_offset, 1)

    @property
    def lockSearchMax(self):
        """Get or set the autolock search range maximum.

        :getter: Return the threshold.
        :setter: Set the threshold.
        :type: :obj:`float`
        """
        return self._autolock['max']

    @lockSearchMax.setter
    def lockSearchMax(self, value):
        try:
            float(value)
        except ValueError:
            raise TypeError('value must be a float or int.')
        if not -10 <= value <= 10:
            raise ValueError('Search maximum has to be between -10 and 10 volts.')
        if value < self._autolock['min']:
            raise ValueError('Please make sure the maximum is greater than the minimum or try setting the minimum first.')
        index_offset = (self._channel - 1) * 5  # the lock state parameter is set on index 1, 6, 12 etc., as each servo channel occupies 5 indices (as of current version)
        self._autolock['max'] = value
        max = _convertVolt2Int(value, self.auxSensitivity, True)
        self._adw.SetData_Long([max], settings.DATA_LOCK, 4 + index_offset, 1)

    @property
    def lockGreater(self):
        """
        Set the lock direction to either greater (True) or lesser (False) than the threshold.

        :getter: Return the current value.
        :setter: Set the condition.
        :type: :obj:`bool`
        """
        return self._autolock['greater']

    @lockGreater.setter
    def lockGreater(self, greater):
        if not isinstance(greater, bool):
            raise TypeError('value must be a bool.')
        index_offset = (self._channel - 1) * 5  # the lock state parameter is set on index 1, 6, 12 etc., as each servo channel occupies 5 indices (as of current version)
        threshold = _convertVolt2Int(self.lockThreshold, self.auxSensitivity, True)
        threshold = general.changeBit(threshold, 16, greater)
        # Sending values to ADwin
        self._adw.SetData_Long([threshold], settings.DATA_LOCK, 2 + index_offset, 1)
        self._autolock['greater'] = greater

    @property
    def relock(self):
        """
        Set the lock to trigger a relock automatically when falling below or above threshold (according to `greater` setting).

        :getter: Return the current value.
        :setter: Set the condition.
        :type: :obj:`bool`
        """
        return self._autolock['relock']

    @relock.setter
    def relock(self, value):
        if not isinstance(value, bool):
            raise TypeError('value must be a bool.')
        self._autolock['relock'] = value

    # @property
    # def snapSw(self):
    #     """
    #     Enable or disable the automatic snapping.
    #
    #     :getter: Return the state of the switch.
    #     :setter: Enable or disable the output.
    #     :type: :obj:`bool`
    #     """
    #     self._readFilterControl()
    #     return self._state['snapSw']
    #
    # @snapSw.setter
    # def snapSw(self, enabled):
    #     if not isinstance(enabled, bool):
    #         raise TypeError('the value must be a bool.')
    #
    #     self._state['snapSw'] = enabled
    #     self._sendFilterControl()
    #
    # @property
    # def snap(self):
    #     """
    #     Set or read the snap limit.
    #
    #     :getter: Return the current limit.
    #     :setter: Set the limit to a value.
    #     :type: :obj:`float`
    #     """
    #     self._snapRead()
    #     return self._snap['limit']
    #
    # @snap.setter
    # def snap(self, value):
    #     try:
    #         float(value)
    #     except ValueError:
    #         raise TypeError('value must be a float or int.')
    #
    #     self._snap['limit'] = value
    #     self.snapSend()
    #
    # @property
    # def snapGreater(self):
    #     """
    #     Set the snap direction to either greater (True) or lesser (False) than the limit.
    #
    #     :getter: Return the current value.
    #     :setter: Set the condition.
    #     :type: :obj:`bool`
    #     """
    #     self._snapRead()
    #     return self._snap['greater']
    #
    # @snapGreater.setter
    # def snapGreater(self, value):
    #     if not isinstance(value, bool):
    #         raise TypeError('value must be a bool.')
    #
    #     self._snap['greater'] = value
    #     self.snapSend()
    #
    # def snapSend(self, limit=None, greater=None):
    #     """
    #     Value to enable locking.
    #
    #     Parameters
    #     ----------
    #     limit: :obj:`float`
    #         Threshold limit to start locking.
    #     greater: :obj:`bool`
    #         Start locking when the aux value is lower or greater than :obj:`limit`.
    #     """
    #     if limit is None:
    #         limit = self._snap['limit']
    #     if greater is None:
    #         greater = self._snap['greater']
    #
    #     try:
    #         float(limit)
    #     except ValueError:
    #         raise TypeError('limit must be a float or int.')
    #     if not isinstance(greater, bool):
    #         raise TypeError('greater must be a bool.')
    #
    #     self._snap['limit'] = limit
    #     self._snap['greater'] = greater
    #
    #     limit = _convertVolt2Int(limit, self.auxSensitivity, True)
    #     limit = general.changeBit(limit, 16, greater)
    #     self._adw.SetData_Long([limit], settings.DATA_SNAP, self._channel, 1)
    #
    # def _snapRead(self):
    #     snapping_config = self._adw.GetData_Long(settings.DATA_SNAP, self._channel, 1)[0]
    #     self._snap['limit'] = _convertInt2Volt(snapping_config & 0xffff, mode=self.auxSensitivity)
    #     self._snap['greater'] = general.readBit(snapping_config, 16)

    @property
    def outputSw(self):
        """
        Enable or disable output switch.

        :getter: Return the state of the switch.
        :setter: Enable or disable the output.
        :type: :obj:`bool`
        """
        self._readFilterControl()
        return self._state['outputSw']

    @outputSw.setter
    def outputSw(self, enabled):
        self._state['outputSw'] = enabled
        self._sendFilterControl()

    @property
    def inputSw(self):
        """
        Enable or disable input switch.

        :getter: Return the state of the switch.
        :setter: Enable or disable the input.
        :type: :obj:`bool`
        """
        self._readFilterControl()
        return self._state['inputSw']

    @inputSw.setter
    def inputSw(self, enabled):
        self._state['inputSw'] = enabled
        self._sendFilterControl()

    @property
    def offset(self):
        """
        Offset value in volt. (-10 to 10)

        :getter: Return the offset value.
        :setter: Set the offset.
        :type: :obj:`float`
        """
        return self._state['offset']

    @offset.setter
    def offset(self, offset):
        limit = round(10 / pow(2, self.inputSensitivity), 2)
        if abs(offset) > limit:
            offset = copysign(limit, offset)
            log.warning('With the selected mode the offset must be in the limits of ±{}V. Adjusting to {}V...'.format(limit, offset))
        self._state['offset'] = offset
        index = self._channel + 8
        offsetInt = _convertVolt2Int(offset, self.inputSensitivity)
        self._adw.SetData_Double([offsetInt], settings.DATA_OFFSETGAIN, index, 1)

    @property
    def gain(self):
        """
        Overall gain factor.

        :getter: Return the gain value.
        :setter: Set the gain.
        :type: :obj:`float`
        """
        return self._state['gain']

    @gain.setter
    def gain(self, gain):
        self._state['gain'] = gain
        index = self._channel
        effectiveGain = 1.0 * self.gain / pow(2, self.inputSensitivity)
        self._adw.SetData_Double([effectiveGain], settings.DATA_OFFSETGAIN, index, 1)

    @property
    def inputSensitivity(self):
        r"""
        Input sensitivity mode (0 to 3).

        The input voltage is amplified by :math:`2^\mathrm{mode}`.

        +------+---------------+------------+
        | mode | amplification | limits (V) |
        +======+===============+============+
        | 0    | 1             | 10         |
        +------+---------------+------------+
        | 1    | 2             | 5          |
        +------+---------------+------------+
        | 2    | 4             | 2.5        |
        +------+---------------+------------+
        | 3    | 8             | 1.25       |
        +------+---------------+------------+

        :getter: Return the sensitivity mode.
        :setter: Set the mode.
        :type: :obj:`int`
        """
        return self._state['inputSensitivity']

    @inputSensitivity.setter
    def inputSensitivity(self, mode):
        if not 0 <= mode <= 3:
            raise Exception('Choose a mode between 0 and 3')

        self._state['inputSensitivity'] = mode

        currentRegister = self._adw.Get_Par(settings.PAR_SENSITIVITY)
        register = general.clearBit(currentRegister, self._channel * 2 - 2)
        register = general.clearBit(register, self._channel * 2 - 1)

        register += mode << self._channel * 2 - 2

        self._adw.Set_Par(settings.PAR_SENSITIVITY, register)

        # Update gain to correct gain change from input sensitivity
        self.gain = self.gain
        self.offset = self.offset

    @property
    def auxSensitivity(self):
        r"""
        Aux sensitivity mode (0 to 3).

        The input voltage is amplified by :math:`2^\mathrm{mode}`.

        +------+---------------+------------+
        | mode | amplification | limits (V) |
        +======+===============+============+
        | 0    | 1             | 10         |
        +------+---------------+------------+
        | 1    | 2             | 5          |
        +------+---------------+------------+
        | 2    | 4             | 2.5        |
        +------+---------------+------------+
        | 3    | 8             | 1.25       |
        +------+---------------+------------+

        :getter: Return the sensitivity mode.
        :setter: Set the mode.
        :type: :obj:`int`
        """
        return self._state['auxSensitivity']

    @auxSensitivity.setter
    def auxSensitivity(self, mode):
        if not 0 <= mode <= 3:
            raise Exception('Choose a mode between 0 and 3')

        self._state['auxSensitivity'] = mode

        currentRegister = self._adw.Get_Par(settings.PAR_SENSITIVITY)
        register = general.clearBit(currentRegister, self._channel * 2 + 14)
        register = general.clearBit(register, self._channel * 2 + 15)

        register += mode << self._channel * 2 + 14

        self._adw.Set_Par(settings.PAR_SENSITIVITY, register)

    @property
    def filters(self):
        """
        All second order sections (SOS) of all filters.

        A neutral filter matrix looks like:

        .. code:: python

            [ [1, 0, 0, 0, 0],
              [1, 0, 0, 0, 0],
              [1, 0, 0, 0, 0],
              [1, 0, 0, 0, 0],
              [1, 0, 0, 0, 0] ]

        Use :obj:`ServoDesign` from :obj:`openqlab.analysis` to create your filters.
        That object you can simply pass to a servo using :obj:`applyServoDesign`.

        :getter: Return all filter values.
        :setter: Write all 5 filters to ADwin and trigger reloading.
        :type: :code:`(5, 5)` matrix with filter values (:obj:`float`).
        """
        return self._state['filters']

    @filters.setter
    def filters(self, filters):
        if not len(filters) == 5:
            raise IndexError('A servo must have exactly 5 filters!')
        self._state['filters'] = filters

        startIndex = (self._channel - 1) * 25 + 1

        data = []
        for f in self._state['filters']:
            for i in f:
                data.append(i)

        self._adw.SetData_Double(data, settings.DATA_FILTERCOEFFS, startIndex, len(data))

        self._triggerReload()

    def applyServoDesign(self, servoDesign=None):
        """
        Apply filters from a :obj:`ServoDesign` object.

        All existing filters of the :obj:`ServoDesign` will be activated directly.

        Parameters
        ----------
        servoDesign: :obj:`openqlab.analysis.ServoDesign`
            Object to apply filters from.
        """
        if servoDesign is None:
            servoDesign = self.servoDesign
        else:
            self.servoDesign = servoDesign
        discreteServoDesign = servoDesign.discrete_form(fs=settings.SAMPLING_RATE)
        filters6 = discreteServoDesign['filters']
        filters = []
        filtersEnabled = []

        # TODO needs refactoring and better testing
        for f in filters6.items():
            filters.append(_rearrange_filter_coeffs(f[1]))
            filtersEnabled.append(True)

        while len(filters) < 5:
            filters.append([1.0, 0, 0, 0, 0])
            filtersEnabled.append(False)

        i = 0
        log.info(servoDesign)
        for f in servoDesign.filters:
            if f is not None:
                filtersEnabled[i] = f.enabled
            i += 1

        self.gain = discreteServoDesign['gain']
        self.filters = filters
        self.filterStates = filtersEnabled

    #########################################
    # Realtime plotting
    #########################################
    def _calculateRefreshTime(self):
        bufferFillingLevel = .5
        if self.rampEnabled:
            bufferFillingLevel = 1

        refreshTime = self._fifo['stepsize'] / settings.SAMPLING_RATE * bufferFillingLevel * self._fifo['maxlen']

        if refreshTime < self.MIN_REFRESH_TIME:
            refreshTime = self.MIN_REFRESH_TIME
        self.realtime['refreshTime'] = refreshTime

    @property
    def _fifoBufferSize(self):
        """Get the current size of the fifo buffer on ADwin."""
        return self._adw.Fifo_Full(settings.DATA_FIFO)

    @property
    def fifoStepsize(self):
        """
        Setter DEPRECATED: Use :obj:`nqontrol.Servo.enableFifo()`

        Trigger ADwin to write the three channels of this servo to the FIFO buffer to read it with the PC over LAN.

        :code:`input`, :code:`aux` and :code:`output` will be sent.

        :getter: Number of program cycles between each data point.
        :setter: Set the number or choose `None` to disable the FiFo output.
        :type: :obj:`int`
        """
        return self._fifo['stepsize']

    @fifoStepsize.setter
    def fifoStepsize(self, stepsize):
        log.warning("DEPRECATED: This setter will be removed in future versions. Use enableFifo().")
        # TODO: Remove the deprecated methods
        if stepsize == 0:
            raise UserInputError('Use None to disable it.')

        if stepsize is not None:
            self.enableFifo(stepsize)
        else:
            self.disableFifo()

    @property
    def realtimeEnabled(self):
        if self.realtime['enabled'] and self.fifoEnabled:
            return True
        else:
            return False

    @property
    def fifoEnabled(self):
        if self._adw.Get_Par(settings.PAR_ACTIVE_CHANNEL) == self._channel:
            return True
        else:
            return False

    def enableFifo(self, stepsize=None, frequency=None):
        """
        Trigger ADwin to write the three channels of this servo to the FIFO buffer to read it with the PC over LAN.

        :code:`input`, :code:`aux` and :code:`output` will be sent.

        Parameters
        ----------
            stepsize: :obj:`int`
                Number of program cycles between each data point.
                If unset it will stay the same or use the default ({})
        """.format(self.DEFAULT_FIFO_STEPSIZE)
        if frequency is not None:
            stepsize = int(frequency / settings.SAMPLING_RATE)
        if stepsize is None:
            stepsize = self._fifo['stepsize']
        if type(stepsize) is not int or stepsize <= 0:
            raise TypeError('The stepsize must be a positive integer.')
        else:
            self._fifo['stepsize'] = stepsize
        # Enable on adwin
        self._adw.Set_Par(settings.PAR_ACTIVE_CHANNEL, self._channel)
        self._adw.Set_Par(settings.PAR_FIFOSTEPSIZE, stepsize)
        # set refresh time
        self._calculateRefreshTime()
        # Create local buffer
        self._createDataFrame()

    def disableFifo(self):
        """Disable the FiFo output if it is enabled on this channel."""
        if self.fifoEnabled:
            # Disable on adwin only if this channel is activated
            self._adw.Set_Par(settings.PAR_ACTIVE_CHANNEL, 0)
            self._adw.Set_Par(settings.PAR_FIFOSTEPSIZE, 0)
            # Destroy local buffer
            self._fifoBuffer = None

    def _readoutNewData(self, n):
        m = self._fifoBufferSize
        if n > m:
            n = m

        newData = DataFrame(columns=self.DEFAULT_COLUMNS)

        if n == 0:
            log.warning('I should readout 0 data.')
            return newData

        # Saving 3 16bit channels in a 64bit long variable
        # Byte    | 7 6 | 5 4   | 3 2 | 1 0    |
        # Channel |     | input | aux | output |
        combined = np.array(self._adw.GetFifo_Double(settings.DATA_FIFO, n)[:], dtype='int')

        def extract_value(combined, offset=0):
            shifted = np.right_shift(combined, offset)
            return np.bitwise_and(shifted, 0xffff)

        log.debug(extract_value(combined[0], 32))
        log.debug(extract_value(combined[0], 16))
        log.debug(extract_value(combined[0]))

        newData['input'] = _convertInt2Volt(extract_value(combined, 32), self._state['inputSensitivity'])
        newData['aux'] = _convertInt2Volt(extract_value(combined, 16), self._state['auxSensitivity'])
        newData['output'] = _convertInt2Volt(extract_value(combined))

        log.debug(newData['input'][0])
        log.debug(newData['aux'][0])
        log.debug(newData['output'][0])

        return newData

    def _prepareContinuousData(self):
        # if we will get speed problems we should implement a more efficient version, e.g. a ring array behaviour.
        n = self._fifoBufferSize
        if n == 0:
            return

        maxlen = self._fifo['maxlen']
        if n >= maxlen:
            n = maxlen
            buf = DataFrame()
        else:
            # local copy of the `maxlen-n` newest entries.
            len_before = len(self._fifoBuffer)
            buf = DataFrame(self._fifoBuffer[n:])
            if self._fifo['maxlen'] < len(buf) + n:
                # import ipdb; ipdb.set_trace()
                raise Exception('That check should not fail. maxlen = {}, len(buf) = {}, len_before = {}, n = {}'.format(self._fifo['maxlen'], len(buf), len_before, n))

        # Read new data
        newData = self._readoutNewData(n)
        # Append to the local DataFrame
        self._fifoBuffer = buf.append(newData, sort=False)

        new_len = len(self._fifoBuffer)
        if new_len > self._fifo['maxlen']:
            raise Exception('That is a bug. Please report it. len(newData): {0}, len(buf): {1}'.format(len(newData), len(buf)))

        dt = self._timeForFifoCycles(1)
        self._fifoBuffer.index = np.arange(0, new_len * dt, dt)[:new_len]

    def _prepareRampData(self, tries=3):
        # TODO: some refactoring...
        # The logic, when to search a new minimum is semi-good
        if tries < 1:
            log.warning('tries must be at least 1.')
            tries = 1

        for i in range(tries):
            log.info("Try {0} of {1}".format(i + 1, tries))
            maxlen = self._fifo['maxlen']
            if self._ramp['minimum'] == 0:
                self._ramp['minimum'] = self._searchRampMinimum()
            if self._ramp['minimum'] is None:
                continue  # Next try when there could not be found a minimum
            # Wait untill we have enough entries
            self._waitForBufferFilling(n=3 * self._fifo['maxlen'])
            # Take data
            newData = self._readoutNewData(3 * self._fifo['maxlen'])
            # Find the first min
            try:
                start = newData.loc[(newData['output'] - self._ramp['minimum']) <= 1e-2].index[0]
                break
            except IndexError:
                log.warning('Could not find a ramp minimum.')
                self._ramp['minimum'] = self._searchRampMinimum()
            except TypeError:
                log.warning('TypeError: {}'.format(self._ramp['minimum']))
            finally:
                if i >= tries - 1:
                    log.warning("Unable to find the ramp minimum {} in {} tries. Giving up...".format(self._ramp['minimum'], tries))
                    return

        # Copy data from the first min untill the end
        localBuffer = DataFrame(newData[start:start + self._fifo['maxlen']])

        # Calculate times for the index
        length = len(localBuffer)
        dt = self._timeForFifoCycles(1)
        localBuffer.index = np.arange(0, length * dt, dt)[:length]

        # print a message if n != maxlen
        # update only if n = maxlen
        if length == maxlen:
            self._fifoBuffer = DataFrame(localBuffer)
        else:
            log.warning('Could not read the correct length of ramp data. It was: {}'.format(len(localBuffer)))

    def _timeForFifoCycles(self, n):
        return n * self._fifo['stepsize'] / settings.SAMPLING_RATE

    def _waitForBufferFilling(self, n=None, refill=True):
        if n is None:
            n = self._fifo['maxlen']
        if refill:
            cycles = n
        else:
            bufferSize = self._fifoBufferSize
            if bufferSize < n:
                cycles = n - bufferSize
            else:
                return
        sleep(self._timeForFifoCycles(cycles))

    def _createDataFrame(self):
        data = {
            'input': [],
            'aux': [],
            'output': [],
        }
        self._fifoBuffer = DataFrame(data=data)

    def _searchRampMinimum(self, tries=6):
        allowed_error = .1 * self._ramp['amplitude']

        for i in range(tries):
            log.info("Try {0} of {1}".format(i + 1, tries))
            self._waitForBufferFilling(n=4 * self._fifo['maxlen'])
            data = self._readoutNewData(2 * self._fifo['maxlen'])

            if len(data) != 2 * self._fifo['maxlen']:
                log.warning("Want to read {} entries, but got {}.".format(2 * self._fifo['maxlen'], len(data)))

            min = data.min()['output']

            if min is None:
                log.warning('Could not find a minimum.')

            if self._ramp['amplitude'] + min < allowed_error:
                log.info('Found the minimum of {}.'.format(min))
                assert min is not None
                return min
            else:
                log.info('The minimum I found, was {}, but it should be {}.'.format(min, -self._ramp['amplitude']))

        log.warning('Could not find the correct minimum after {0} tries. The method should be optimized if it happens often.'.format(tries))
        return None

    def _prepareData(self):
        """Return new data from ADwin."""
        if not self.fifoEnabled:
            log.warning('The FiFo output was not activated. Enabling now...')
            self.enableFifo()
        if self.rampEnabled:
            self._prepareRampData()
        else:
            self._prepareContinuousData()
        return self._fifoBuffer[self.realtime['ydata']]

    def _realtimeLoop(self):
        # plotting loop
        assert(self.realtimeEnabled), 'Realtime should be enabled when starting the loop.'

        # generate plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.ion()  # interactive mode

        try:
            while self.realtimeEnabled:
                timeStart = time()
                ax.clear()
                if self.realtime['ylim'] is None:
                    ax.set_ylim(auto=True)
                else:
                    ax.set_ylim(self.realtime['ylim'])
                ax.plot(self._prepareData())
                ax.legend(self.realtime['ydata'], loc=1)

                timePause = self.realtime['refreshTime'] - time() + timeStart
                if timePause <= 0:
                    timePause = 1e-6

                plt.pause(timePause)
        except (KeyboardInterrupt, TclError):
            plt.close('all')
            log.info('Plot closed')
        finally:
            # Ensure that `realtime` is disabled if the plot is closed
            log.info('Stop plotting...')
            self.realtime['enabled'] = False
            self._subProcess = None

    def stopRealtimePlot(self):
        """Stop the realtime plot."""
        self.realtime['enabled'] = False
        if self._subProcess is not None:
            self._subProcess.join()
        assert not self._subProcess.is_alive(), 'The subprocess should be finished!'

    def realtimePlot(self, ydata=None, refreshTime=None, multiprocessing=True):
        """
        Enable parallel realtime plotting.

        To stop the running job call `stopRealtimePlot()`.

        Parameters
        ----------
        ydata: :obj:`list` of :obj:`str`
            Choose the data to be plotted: :code:`['input', 'aux', 'output']`.
        refreshTime: :obj:`float`
            Sleeping time (s) between plot updates.
        """
        if (self._subProcess is not None and self._subProcess.is_alive()):
            raise UserInputError('Do you really want more than one plot of the same data? It is not implemented...')
        if self._fifoBuffer is None:
            log.info('Enabling the FiFo buffer with a default step size of {}...'.format(self.DEFAULT_FIFO_STEPSIZE))
            self.enableFifo()

        # Update local parameters
        self.realtime['enabled'] = True
        if ydata:
            self.realtime['ydata'] = ydata
        if refreshTime:
            self.realtime['refreshTime'] = refreshTime

        # Start plotting process
        if multiprocessing:
            self._subProcess = mp.Process(target=self._realtimeLoop)
            self._subProcess.start()
        else:
            self._realtimeLoop()

    ########################################
    # Temperature feedback
    ########################################
    @property
    def tempFeedback(self):
        """The temperature feedback server associated with the servo.

        :getter: Return the :obj:`FeedbackController`.
        :setter: Set a new :obj:`FeedbackController`.
        :type: :obj:`FeedbackController`.
        """
        return self._tempFeedback

    def tempFeedbackStart(self, dT=None, mtd=None, voltage_limit=None, server=settings.DEFAULT_TEMP_HOST, port=settings.DEFAULT_TEMP_PORT, update_interval=None):
        """Start the temperature feedback server. Setup a server if it hasn't been previously set.

        Parameters
        ----------
        dT : :obj:`float`
            Description of parameter `dT`.
        mtd : :obj:`tuple`
            (1, 1)
        voltage_limit : :obj:`float`
            The maximum voltage to which one can go using the temperature control (the default is 5).
        server : type
            Description of parameter `server` (the default is settings.DEFAULT_TEMP_HOST).
        port : type
            Description of parameter `port` (the default is settings.DEFAULT_TEMP_PORT).
        update_interval : :obj:`float`
            Description of parameter `update_interval` (the default is 1).

        """
        if dT is None:
            dT = self._tempFeedbackSettings['dT']
        if mtd is None:
            mtd = self._tempFeedbackSettings['mtd']
        if voltage_limit is None:
            voltage_limit = self._tempFeedbackSettings['voltage_limit']
        if update_interval is None:
            update_interval = self._tempFeedbackSettings['update_interval']

        if self._tempFeedback is None:
            self._tempFeedback = FeedbackController(self, dT, mtd, voltage_limit, server, port, update_interval)
        else:
            self.tempFeedback.dT = dT
            self.tempFeedback.mtd = mtd
            self.tempFeedback.voltage_limit = voltage_limit
            self.tempFeedback.update_interval = update_interval
        self.tempFeedback.start()

    def tempFeedbackStop(self):
        self.tempFeedback.enabled = False
        self.tempFeedback.join()
        self._tempFeedback = None

    ########################################
    # Save and load settings
    ########################################
    def _applySettingsDict(self, data):
        # Don't import the channel because it isn't possible to change it.
        DONT_SERIALIZE = self.DONT_SERIALIZE + ['_channel']
        for d in self.__dict__:
            value = data.get(d.__str__())
            if (d.__str__() not in DONT_SERIALIZE) and (value is not None):
                if d.__str__() in self.JSONPICKLE:
                    self.__dict__[d.__str__()] = jsonpickle.decode(value)
                elif type(value) is dict:
                    self.__dict__[d.__str__()].update(value)
                else:
                    self.__dict__[d.__str__()] = value

    def getSettingsDict(self):
        """
        Get a dict with all servo settings.

        Returns
        -------
        :obj:`dict`
            Return all important settings for the current servo state.
        """
        data = {}
        for d in self.__dict__:
            if d.__str__() not in self.DONT_SERIALIZE:
                value = self.__dict__[d.__str__()]
                # Convert dicts from multiprocessing
                if type(value) is mp.managers.DictProxy:
                    value = dict(value)
                elif d.__str__() in self.JSONPICKLE:
                    value = jsonpickle.encode(value)
                data[d.__str__()] = value
        return data

    def saveJsonToFile(self, filename):
        """
        Save this single servo as json to a file.

        Parameters
        ----------
        filename: :obj:`str`
            Filename to save the json file.
        """
        data = {
            self.__class__.__name__: self.getSettingsDict()
        }
        with open(filename, 'w+') as file:
            json.dump(data, file, indent=2)

    def loadSettings(self, applySettings):
        """
        Load settings from file or dict.

        Not reading the channel, it can only be set on creating a servo object.

        Parameters
        ----------
        applySettings: :obj:`str` or :obj:`dict`
            Settings to load for this servo.
        """
        if type(applySettings) is dict:
            settings = applySettings
        elif type(applySettings) is str:
            settings = self._readJsonFromFile(applySettings)
        else:
            raise Exception('You can only apply settings from a file or a dict.')

        self._applySettingsDict(settings)
        self._sendAllToAdwin()

    def _readJsonFromFile(self, filename):
        """
        Read settings from a single servo file.

        return: dict with only the servo settings
        """
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
        except FileNotFoundError as e:
            raise e

        if not data.get(self.__class__.__name__):
            raise Exception('Invalid file.')

        return data[self.__class__.__name__]

    ########################################
    # Autolock
    ########################################
    def autolock(self, lock, threshold=None, min=None, max=None, greater=None, relock=None):
        if not isinstance(lock, int):
            raise TypeError('lock has to be an integer.')
        if lock not in range(2):
            raise ValueError('The lock state is given using integers, where `0: autolock-off`, `1: start/search-peak`, `2: lock-mode`. The user input should either be `0` or `1`, as the rest ist determined by the locking algorithm.')
        if threshold is None:
            threshold = self._autolock['threshold']
        if min is None:
            min = self.lockSearchMin
        if max is None:
            max = self.lockSearchMax
        if greater is None:
            greater = self.lockGreater
        if relock is None:
            relock = self.relock
        if not isinstance(greater, bool):
            raise TypeError('greater must be a bool.')
        if not isinstance(relock, bool):
            raise TypeError('greater must be a bool.')
        try:
            float(threshold)
            float(min)
            float(max)
        except ValueError:
            raise TypeError('parameters must be floats or ints.')
        self._autolock['state'] = lock

        # disable ramp when locking (should be disabled by the GUI, this is mostly for use with a terminal)
        if lock and self.rampEnabled:
            self.disableRamp()

        # disabling input and output while searching
        if lock:
            self.outputSw = False
            self.inputSw = False
        else:
            self.inputSw = True
            self.outputSw = True

        index_offset = (self._channel - 1) * 5  # the lock state parameter is set on index 1, 6, 12 etc., as each servo channel occupies 5 indices (as of current version)
        # the fifth array index is occupied by the a "lastFound" value, which can be use in case of a relock. it is set within the autolock, not as part of the python program

        # set lockmode to 0 while sending new parameters
        self._adw.SetData_Long([0], settings.DATA_LOCK, 1 + index_offset, 1)
        # send all values to ADwin
        self.lockSearchMin = min
        self.lockSearchMax = max
        self.lockThreshold = threshold
        self.lockGreater = greater
        self.relock = relock
        lock = general.changeBit(lock, 2, relock)  # adding relock bit
        # activating lock
        self._adw.SetData_Long([lock], settings.DATA_LOCK, 1 + index_offset, 1)  # setting the lock state last


class FeedbackController(Thread):
    def __init__(self, servo, dT, mtd, voltage_limit, server, port, update_interval=1):
        mtd = tuple(mtd)
        if not isinstance(mtd, tuple) and len(mtd) == 2:
            raise ValueError('The parameter mtd must be a tuple with port and mtd number.')

        Thread.__init__(self)
        self._server = server
        self._port = port
        self._servo = servo
        self._dT = dT
        self._mtd = mtd
        self._voltage_limit = voltage_limit
        self._update_interval = update_interval
        self.enabled = True
        self.last_answer = ''

        self._servo._tempFeedbackSettings.update({
            'dT': dT,
            'mtd': mtd,
            'voltage_limit': voltage_limit,
            'update_interval': update_interval,
        })

    @property
    def dT(self):
        return self._dT

    @dT.setter
    def dT(self, value):
        self._dT = value
        self._servo._tempFeedbackSettings['dT'] = value

    @property
    def mtd(self):
        return self._mtd

    @mtd.setter
    def mtd(self, value):
        value = tuple(value)
        self._mtd = value
        self._servo._tempFeedbackSettings['mtd'] = value

    @property
    def voltage_limit(self):
        return self._voltage_limit

    @voltage_limit.setter
    def voltage_limit(self, value):
        self._voltage_limit = value
        self._servo._tempFeedbackSettings['voltage_limit'] = value

    @property
    def update_interval(self):
        return self._update_interval

    @update_interval.setter
    def update_interval(self, value):
        self._update_interval = value
        self._servo._tempFeedbackSettings['update_interval'] = value

    def _send(self, feedback):
        socket = create_connection(f'ws://{self._server}:{self._port}')
        socket.send(f'mtd:{self.mtd[0]},{self.mtd[1]}:{feedback}')
        answer = socket.recv()
        self.last_answer = answer
        socket.close()
        return answer

    def _calculateFeedback(self, voltage):
        return self.dT * voltage / 10

    def _checkConditions(self):
        return not self._servo.rampEnabled

    def _last_output(self):
        out = self._servo._adw.GetData_Long(4, self._servo._channel, 1)[0]
        return _convertInt2Volt(out)

    def run(self):
        while self.enabled:
            if self._checkConditions():
                output = self._last_output()
                if abs(output) >= self.voltage_limit:
                    feedback = self._calculateFeedback(output)
                    answer = self._send(feedback)
                    if 'OK.' in answer:
                        log.info(answer)
                    else:
                        log.warning(answer)
            sleep(self.update_interval)
