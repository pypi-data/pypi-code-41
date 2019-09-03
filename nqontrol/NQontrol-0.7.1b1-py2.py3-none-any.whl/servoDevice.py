"""ServoDevice."""

import os
import sys
from ADwin import ADwin, ADwinError
from nqontrol.mockAdwin import MockADwin
from nqontrol.servo import Servo
import json
import logging as log
from openqlab.analysis.servo_design import ServoDesign
import jsonpickle
from nqontrol import settings
from shutil import copyfile
from datetime import datetime


class ServoDevice:
    """
    A ServoDevice is the whole device, containing 8 (default can be changed) single servos.

    With this object you can control one ADwin device and manage all servos of this device.

    Parameters
    ----------
    deviceNumber: :obj:`int`
        Number of the ADwin device on this system.
        The number can be skipped when loading a ServoDevice from file.

        You have to set it using the tool `adconfig`.
        See [installation](install) for configuration details.
    readFromFile: :obj:`str`
        Select a filename if you want to open a whole ServoDevice with all servos from a saved json file.
    process: :obj:`str`
        If you have a compiled special version of the basic program running on ADwin, you can select a custom binary.
    """

    DONT_SERIALIZE = ['adw', '_servos', 'deviceNumber']
    DEFAULT_PROCESS = "nqontrol.TC1"
    JSONPICKLE = ['_servoDesign']
    # Path of the compiled binary. It comes usually with the source code, but can be exchanged.

    def __init__(self, deviceNumber=None,
                 readFromFile=None,
                 process=DEFAULT_PROCESS,
                 reboot=False):
        """Create a new ServoDevice object."""
        raiseExceptions = 1
        if deviceNumber == 0:
            log.warning('Running with mock device!')
            self.adw = MockADwin(deviceNumber)
        else:
            self.adw = ADwin(deviceNumber, raiseExceptions)
        self._servoDesign: ServoDesign = ServoDesign()  # The dummy servo design object
        self._servos = [None] * settings.NUMBER_OF_SERVOS
        self.deviceNumber = deviceNumber

        self._monitors = [None] * settings.NUMBER_OF_MONITORS

        try:
            self._bootAdwin(process, reboot=reboot)
        except ADwinError as e:
            if e.errorNumber == 2001:
                log.warning('No device connected! Starting with mock device!')
            log.error(e.errorNumber)
            self.adw = MockADwin(deviceNumber)
            self._bootAdwin(process)

        # Adding servos
        names = settings.SERVO_NAMES
        for i in range(1, settings.NUMBER_OF_SERVOS + 1):
            # Check if a servo name is set in SETTINGS
            if (deviceNumber in names) and (i in names[deviceNumber]):
                self.addServo(channel=i, name=names[deviceNumber][i])
            else:
                self.addServo(channel=i)

        if readFromFile and os.path.isfile(readFromFile):
            log.info('Loaded from: ' + readFromFile)
            self.loadDeviceFromJson(readFromFile)

        if self.deviceNumber is None:
            raise Exception('You have to set a deviceNumber if you do not load a ServoDevice from a file!')

    @property
    def servoDesign(self) -> ServoDesign:
        """
        Return the dummy ServoDesign object associated with the device.

        :getter: The ServoDesign object.
        :type: :obj:`openqlab.analysis.servo_design.ServoDesign`
        """
        return self._servoDesign

    @property
    def monitors(self):
        """
        Return the list of parameters monitor configurations of the device.

        :getter: List of monitor parameters. Each entry is a list containing servo index and card String.
        :setter: Set the list of parameters for ADwin monitor channels.
        :type: :obj:`list`
        """
        return self._monitors

    @monitors.setter
    def monitors(self, monitors):
        self._monitors = monitors

    @property
    def workload(self):
        """
        Get the current workload of the ADwin device.

        :getter: CPU load (0 to 100).
        :type:  :obj:`int`
        """
        return int(self.adw.Workload())

    @property
    def timestamp(self):
        """
        Get the current time stamp of the ADwin device.

        It is a counter that ist started on booting and counts the runtime in seconds.
        It is mainly a debugging feature to see that the device is running.

        :getter: Runtime in seconds.
        :type:  :obj:`int`
        """
        return int(self.adw.Get_Par(settings.PAR_TIMER))

    @property
    def rampEnabled(self):
        """
        Check ADwin if the ramp is enabled on a channel.

        :getter: :obj:`False` if disabled, channel number if enabled.
        :type: :obj:`False` or :obj:`int`
        """
        control = self.adw.Get_Par(settings.PAR_RCR)
        channel = control & 15
        if channel > 0:
            return channel
        else:
            return 0  # 0 is now the false channel

    def _bootAdwin(self,
                   process=DEFAULT_PROCESS,
                   reboot=False):
        """Boot ADwin if necessary."""
        # Firmware that is needed to boot an ADwin with T12 CPU
        firmware = "ADwin12.btl"
        # Making the boot platform independent
        if sys.platform == 'win32':
            btl = self.adw.ADwindir + firmware
        else:
            btl = self.adw.ADwindir + '/share/btl/' + firmware

        if reboot:
            self.adw.Boot(btl)
        else:
            # Hack to check if the ADwin is booted.
            # It throws a timeout error with the number 2 if it has not.
            try:
                self.adw.Workload()
            except ADwinError as e:
                if e.errorNumber == 2:
                    # Boot the device
                    self.adw.Boot(btl)

        try:
            if self.adw.Process_Status(1) == 0:
                # change to script directory to load the default binary
                abspath = os.path.abspath(__file__)
                dirname = os.path.dirname(abspath)
                os.chdir(dirname)
                # Start the control process
                self.adw.Load_Process(process)
                self.adw.Start_Process(1)
        except ADwinError as e:
            log.error("There is something strange with the ADwin connection. Rebooting the device should help.")
            raise e

    def printDevice(self):
        return 'Device ' + str(self.getDeviceNumber)

    def reboot(self):
        """Make a reboot of the ADwin device."""
        self._bootAdwin(reboot=True)
        self._sendAllToAdwin()
        for s in self._servos:
            if s is not None:
                s._sendAllToAdwin()

    def servo(self, channel):
        """
        Get the servo of the selected physical channel to control it directly.

        Parameters
        ----------
        channel: :obj:`int`
            Physical channel from 1 to {}.

        Returns
        -------
        :obj:`Servo`
            Servo object.
        """.format(settings.NUMBER_OF_SERVOS)
        return self._servos[channel - 1]

    def servo_iterator(self):
        for s in self._servos:
            yield s

    def list_servos(self):
        print(self._list_servos_str())

    def _list_servos_str(self):
        str = f'ServoDevice {self.deviceNumber}\n'
        for s in self.servo_iterator():
            str += f'  Servo {s.channel}: {s.name}\n'
        return str

    def addServo(self, channel, applySettings=None, name=None):
        """
        Add a new servo to be able to control it.

        Parameters
        ----------
        channel: :obj:`int`
            Physical channel from 1 to {}.
        applySettings: :obj:`str` or :obj:`dict`
            You can directly apply settings from a json file or a dict.
        """.format(settings.NUMBER_OF_SERVOS)
        if channel > settings.NUMBER_OF_SERVOS or channel < 1:
            raise IndexError("Choose a channel from 1 to {}!".format(settings.NUMBER_OF_SERVOS))
        if self._servos[channel - 1] is None:
            self._servos[channel - 1] = Servo(channel, self.adw, applySettings=applySettings, name=name)
        else:
            raise IndexError("A servo on this channel does already exist!")

    def removeServo(self, channel):
        """
        Remove a servo from the device object and stop controlling it.

        Parameters
        ----------
        channel: :obj:`int`
            Number of the physical channel to remove from 1 to {}.
        """.format(settings.NUMBER_OF_SERVOS)
        self._servos[channel - 1] = None

    def disableMonitor(self, monitor_channel):
        """
        Disable the selected monitor channel.

        Parameters
        ----------
        monitor_channel: :obj:`int`
            Channel to disable the output.
        """
        self.monitors[monitor_channel - 1] = None
        self.adw.SetData_Long([0], settings.DATA_MONITORS, monitor_channel, 1)

    def enableMonitor(self, monitor_channel, servo, card):
        """
        Enable the monitor output on the hardware channel `monitor_channel` for a given Servo.

        Parameters
        ----------
        monitor_channel: :obj:`int`
            Select the channel on the ADwin D/A card (1 to 8).
        servo: :obj:`int`
            The index of the Servo which will be assigned to the monitor channel.
        card: :obj:`str`
            Choose one of the possible cards a servo has control over: 'input', 'aux', 'output' or 'ttl'.
        """
        if monitor_channel < 1 or monitor_channel > 8:
            raise IndexError('Use a channel from 1 to 8, not "'
                             + str(monitor_channel) + '"!')

        if card == 'input':
            monitor = servo
        elif card == 'aux':
            monitor = servo + 8
        elif card == 'output':
            monitor = servo + 20
        elif card == 'ttl':
            monitor = 30
        else:
            raise ValueError('You should choose one of the possible cards for the monitor output.')

        self.monitors[monitor_channel - 1] = dict({'servo': servo, 'card': card})
        self.adw.SetData_Long([monitor], settings.DATA_MONITORS, monitor_channel, 1)

    def _backupSettingsFile(self, filename):
        if os.path.isfile(filename):
            timestamp = datetime.now().strftime(settings.BACKUP_SUBSTRING)
            filename_base, extension = os.path.splitext(filename)
            backup = "{}.{}{}".format(filename_base, timestamp, extension)

            if os.path.isfile(backup):
                log.error('The filename of the backup does already exist.')
                raise IOError('The filename of the backup does already exist. Not overwriting the old backup...')

            try:
                copyfile(filename, backup)
                log.warning('Created backup file at {}.'.format(backup))
            except (IOError, OSError) as e:
                log.error(e)
                raise e

    def _writeSettingsToFile(self, filename, data):
        if settings.CREATE_SETTINGS_BACKUP:
            self._backupSettingsFile(filename)
        with open(filename, 'w+') as file:
            json.dump(data, file, indent=2)

    def saveDeviceToJson(self, filename=settings.SETTINGS_FILE):
        """
        Save the settings of this device and all servos to a json file.

        Parameters
        ----------
        filename: :obj:`str`
            Filename of the output file.
            It will be overwritten without asking.
        """
        data = {
            self.__class__.__name__: {
                'deviceNumber': self.deviceNumber,
                '_monitors': self.monitors,
                '_servoDesign': jsonpickle.encode(self.servoDesign),
                '_servos': {}
            }
        }
        for s in self._servos:
            if s is not None:
                servoName = s.__class__.__name__ + "_" + str(s._channel)
                data[self.__class__.__name__]['_servos'][servoName] = s.getSettingsDict()

        if os.path.splitext(filename)[1] == '':
            filename = filename + '.json'
        self._writeSettingsToFile(filename, data)

    def loadServoFromJson(self, channel, applySettings):
        """
        Load settings directly to a new or existing :obj:`Servo`.

        All existing settings on this channel will be overwritten.

        Parameters
        ----------
        channel: :obj:`int`
            Physical channel from 1 to {}.
        applySettings: :obj:`str` or :obj:`dict`
            Settings to apply to the selected :obj:`Servo`.
        """.format(settings.NUMBER_OF_SERVOS)
        self.servo(channel).loadSettings(applySettings)

    def loadDeviceFromJson(self, filename=settings.SETTINGS_FILE):
        """
        Load a device with all servos from json file.

        Read the `deviceNumber` only if it is called from the constructor,
        because it can not be changed for an existing :obj:`ServoDevice`.

        Parameters
        ----------
        filename: :obj:`str`
            Filename with a saved :obj:`ServoDevice` state.
        """
        # load them from json
        with open(filename, 'r') as file:
            data = json.load(file)
        if not data.get(self.__class__.__name__):
            raise Exception('Wrong file format.')
        if self.deviceNumber is None:
            self.deviceNumber = data[self.__class__.__name__]['deviceNumber']

        # loading servo settings
        servos = data[self.__class__.__name__]['_servos']
        for s in servos:
            channel = servos[s]['_channel']
            if channel <= settings.NUMBER_OF_SERVOS:
                self.loadServoFromJson(channel, servos[s])

        # Loading device parameters
        self._applySettingsDict(data)
        self._sendAllToAdwin()

    def _sendAllToAdwin(self):
        """Write all settings to ADwin."""
        # Enabling all monitors contained in the save
        for i, monitor in enumerate(self.monitors):
            if monitor is not None:
                self.enableMonitor(i + 1, monitor['servo'], monitor['card'])

    def _applySettingsDict(self, data):
        data = data[self.__class__.__name__]
        DONT_SERIALIZE = self.DONT_SERIALIZE
        for d in self.__dict__:
            value = data.get(d.__str__())
            if (d.__str__() not in DONT_SERIALIZE) and (value is not None):
                if d.__str__() in self.JSONPICKLE:
                    value = jsonpickle.decode(value)
                self.__dict__[d.__str__()] = value
