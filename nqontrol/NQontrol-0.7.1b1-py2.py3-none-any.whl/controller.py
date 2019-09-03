"""The main module handling interaction of an ADwin interface and a browser based Dash UI.
The main class handling the ADwin is :obj:`nqontrol.servoDevice.ServoDevice`.

All init/loadFromSave functions start with `get`.

All callback functions handling user interaction start with `call`.

"""
from nqontrol import settings
from nqontrol.servoDevice import ServoDevice
from nqontrol.errors import ConfigurationError
import plotly.graph_objs as go
from plotly import subplots
from ADwin import ADwinError
from dash.exceptions import PreventUpdate
from fastnumbers import fast_real, fast_int
from openqlab.analysis.servo_design import Filter
from openqlab import io
import base64
import datetime
import logging as log

if settings.DEVICES_LIST:
    DEVICES = [ServoDevice(deviceNumber=i, readFromFile=settings.SETTINGS_FILE)
               for i in settings.DEVICES_LIST]
else:
    raise ConfigurationError('No device specified and no save file provided.')


#
#
#
# INFORMATION GETTERS FOR UI - INIT / LOAD FUNCTIONS
# All methods that are fired on initial startup, initializing to default or loading from Save.
# These functions are not associated with a callback
#
#
#
def getCurrentSaveName():
    """Return name of save file as string if one has been specified.

    Concerns the header section of the UI.

    Returns
    -------
    :obj:`String`
        Name of the save file or empty string

    """
    if settings.SETTINGS_FILE is not None:
        return settings.SETTINGS_FILE
    return ''


def getServoName(deviceNumber, servoNumber):
    """Return name attribute of servo: :obj:`servo.name` from Save or if specified in `settings.py`.

    Concerns the servo section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`String`
        :obj:`servo.name`

    """
    servo = device(deviceNumber).servo(servoNumber)
    return servo.name


def getMaxFilters(deviceNumber):
    """Return the maximum number of filters for the :obj:`ServoDevice.servoDesign`.

    This is a used multiple times in the UI and not part of a specific component.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`int`
        Maximum number of filters for the associated :obj:`ServoDesign`.

    """
    servoDesign = device(deviceNumber).servoDesign
    return servoDesign.MAX_FILTERS


def getCurrentRampLocation(deviceNumber):
    """Return current channel of ADwin ramp from save. Default is None.

    Concerns the header section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`int`
        Channel number of :obj:`servo` on which ramp is active.

    """
    return device(deviceNumber).rampEnabled


def getInputStates(deviceNumber, servoNumber):
    """Return a list of enabled input channels. Either from save or default (empty).

    Concerns the servo section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        Specifies the :obj:`nqontrol.ServoDevice.deviceNumber`.
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`list`
        List containing names as strings.

    """
    checklist = []
    servo = device(deviceNumber).servo(servoNumber)
    if servo.inputSw:
        checklist.append('input')
    if servo.offsetSw:
        checklist.append('offset')
    return checklist


def getOffset(deviceNumber, servoNumber):
    """Return the servo's saved or default offset.

    Concerns the servo section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        :obj:`servo.offset`

    """
    return device(deviceNumber).servo(servoNumber).offset


def getGain(deviceNumber, servoNumber):
    """Return servo's saved or default gain.

    Concerns the servo section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        :obj:`servo.gain`

    """
    return device(deviceNumber).servo(servoNumber).gain


def getActiveFilters(deviceNumber, servoNumber):
    """Return list of active filters for filter-checklist.
    Load from save file or default empty list.
    The checklist is part of the servo section.
    Filter labels are loaded in :obj:`controller.getFilterLabels()`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`list`
        List containing indices of active filters.

    """
    filters = device(deviceNumber).servo(servoNumber).servoDesign._filters
    active = []
    for i, filter in enumerate(filters):
        if filter is not None and filter.enabled:
            active.append(i)
    return active


def getFilterLabels(deviceNumber, servoNumber):
    """List containing filter-checklist labels (objects) as used by `Dash`.

    The checklist labels contain the short description of filters or default to `Filter {index}`.
    The checklist is part of the servo section.
    Filter states are loaded in :obj:`controller.getActiveFilters()`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`list`
        List of labels.

    """
    labels = []
    servo = device(deviceNumber).servo(servoNumber)
    servoDesign = servo.servoDesign
    for i in range(servoDesign.MAX_FILTERS):
        filter = servoDesign.get(i)
        if filter is not None:
            labels.append(filter.description)
        else:
            labels.append('Filter {}'.format(i))
    return [{'label': labels[i], 'value': i} for i in range(servoDesign.MAX_FILTERS)]


def getFilterEnabled(deviceNumber, filterIndex):
    """Load state of an individual filter.

    The UI in the second order section requires individual checkboxes, thus,
    filter states have to be loaded individually.

    Returns a list which is either empty or contains the filter index,
    signifying whether it is active or not (Checkbox UI elements work only with lists).
    The default state for a None filter however is active.
    So the only case in which the checkbox is set to inactive if an inactive filter is specified.

    This loads a state for the Second Order Section of the UI, not the servo sections!
    The getters for the servo section are :obj:`controller.getActiveFilters()`
    and :obj:`controller.getFiltersEnabled()`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`list`
        List containing the filter index or empty list.

    """
    filter = device(deviceNumber).servoDesign.get(filterIndex)
    if filter is not None:
        if not filter.enabled:
            return []
    return [filterIndex]


def getFilterDropdown(deviceNumber, filterIndex):
    """Initialize the dropdown state of the filter UI for given index.
    If empty return None. Concerns the Second Order Section of the UI,
    not the servo's filter section!

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`String`
        Name of the active filter class. None if inactive.

    """
    filter = device(deviceNumber).servoDesign.get(filterIndex)
    if filter is not None:
        return filter.__class__.__name__
    return None


def getFilterMainPar(deviceNumber, filterIndex):
    """Initialize the main parameter of the filter UI for given index.
    If no filter exists at given index return None.
    Concerns the Second Order Section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        Parameter as a float or None.

    """
    filter = device(deviceNumber).servoDesign.get(filterIndex)
    if filter is not None:
        return filter._cF
    return None


def getFilterSecondPar(deviceNumber, filterIndex):
    """Initialize the second parameter of the filter UI for given index.
    If no filter exists at given index return None.
    Concerns the Second Order Section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        Secondary parameter as float or None.

    """
    filter = device(deviceNumber).servoDesign.get(filterIndex)
    if filter is not None:
        return filter.second_parameter
    return None


def getFilterDescription(deviceNumber, filterIndex):
    """Initialize the description of the filter UI for given index.
    If no filter exists at given index return None.
    Concerns the Second Order Section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`String`
        Filter description as a string or None.

    """
    filter = device(deviceNumber).servoDesign.get(filterIndex)
    if filter is not None:
        return filter.description
    return None


def getOutputStates(deviceNumber, servoNumber):
    """Return a list of enabled output channels. Either from save or default (empty).

    Concerns the servo section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`list`
        List containing names as strings.
    """
    checklist = []
    servo = device(deviceNumber).servo(servoNumber)
    if servo.auxSw:
        checklist.append('aux')
    # if servo.snapSw:
    #     checklist.append('snap')
    if servo.outputSw:
        checklist.append('output')
    return checklist


def getServoAmplitude(deviceNumber, servoNumber):
    """Return the ramp amplitude setting for the specified :obj:`servo`.
    Load from save or default to `0.1`.

    Concerns the servo ramp section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        Amplitude as float.

    """
    servo = device(deviceNumber).servo(servoNumber)
    amplitude = servo.rampAmplitude
    return amplitude


def getServoFrequency(deviceNumber, servoNumber):
    """Return the ramp frequency setting for specified :obj:`servo`.
    Load from save or defaukt to `20`.

    Concerns the servo ramp section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    type
        Description of returned object.

    """
    servo = device(deviceNumber).servo(servoNumber)
    frequency = servo.rampFrequency
    return frequency


def getServoMinFrequency(deviceNumber, servoNumber):
    """Return the minimum ramp frequency of the specified :obj:`servo`.
    This is a default value resulting from the ADwin variables in the `settings.py`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        Minimum ramp frequency.

    """
    return device(deviceNumber).servo(servoNumber).rampFrequencyMin


def getServoMaxFrequency(deviceNumber, servoNumber):
    """Return the maximum ramp frequency of the specified :obj:`servo`.
    This is a default value resulting from the ADwin variables in the `settings.py`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        Maximum ramp frequency.

    """
    return device(deviceNumber).servo(servoNumber).rampFrequencyMax


def getServoFrequencyStep(deviceNumber, servoNumber):
    """Calculate the frequency steps for UI slider of the UI's servo ramp section.
    Results from ADwin variables in `settings.py`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        Step value as float.

    """
    servo = device(deviceNumber).servo(servoNumber)
    step = (servo.rampFrequencyMax - servo.rampFrequencyMin) / 254
    return step


def getInputSensitivity(deviceNumber, servoNumber):
    """Return :obj:`servo.inputSensitivity`.
    Since each servo outputs 16 bit this basically relates to 'accuracy'.
    Please read the official docs for more information on how-to-use.

    Concerns the servo section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        :obj:`servo.inputSensitivity`

    """
    servo = device(deviceNumber).servo(servoNumber)
    return servo.inputSensitivity


def getAuxSensitivity(deviceNumber, servoNumber):
    """Return :obj:`servo.auxSensitivity`.
    Since each servo outputs 16 bit this basically relates to 'accuracy'.
    Please read the official docs for more information on how-to-use.

    Concerns the servo section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`float`
        :obj:`servo.auxSensitivity`

    """
    servo = device(deviceNumber).servo(servoNumber)
    return servo.auxSensitivity


def getMonitorsServo(deviceNumber, channel):
    """Return the target of a monitor channel.
    A servo channel can be assigned to one of {} monitor channels.

    Concerns the monitor section of the UI.
    Please note that this does not relate to the live graph of the UI
    but to the hardware monitor channels on the ADwin.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`int`
        Monitor channel index or None.

    """.format(settings.NUMBER_OF_MONITORS)
    dev = device(deviceNumber)
    channelData = dev.monitors[channel - 1]
    # channel data is either a dict or None
    if channelData is not None:
        return channelData['servo']
    else:
        return channelData


def getMonitorsCard(deviceNumber, channel):
    """Return the card of a monitor channel.
    One of 'input', 'aux', 'output', 'ttl' or `None`.
    A servo channel can be assigned to one of {} monitor channels.

    Concerns the monitor section of the UI.
    Please note that this does not relate to the live graph of the UI
    but to the hardware monitor channels on the ADwin.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`String`
        Card specifier or `None`.

    """.format(settings.NUMBER_OF_MONITORS)
    dev = device(deviceNumber)
    channelData = dev.monitors[channel - 1]
    if channelData is not None:
        return channelData['card']
    else:
        return channelData


def getSDGain(deviceNumber):
    """Return :obj:`ServoDevice.servoDesign.gain`,
    the gain of the :obj:`ServoDesign` associated with the device.

    Concerns the Second Order Section of the UI.

    Please note that functionality wise this equates to :obj:`servo.gain`
    if a :obj:`ServoDesign` is applied to a servo.
    The servo and ServoDesign then share a gain.
    The Second Order Section of the UI thus needs a separate input to prevent
    override to default when applying. Please read the documentation for further information.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`float`
        Gain of the device's :obj:`ServoDesign` as a float.

    """
    servoDesign = device(deviceNumber).servoDesign
    return servoDesign.gain


# def getSnapLimit(deviceNumber, servo):
#     """Return the initial value of the snap voltage limit of a servo. Part of the servo section.
#
#     Parameters
#     ----------
#     deviceNumber : :obj:`int`
#         :obj:`ServoDevice.deviceNumber`
#     servo : :obj:`int`
#         Servo index :obj:`servo.channel`
#
#     Returns
#     -------
#     :obj:`float`
#         The snap voltage limit as a float.
#
#     """
#     servo = device(deviceNumber).servo(servo)
#     return servo.snap
#
#
# def getSnapGreater(deviceNumber, servo):
#     """Return the initial value of the snap condition of a servo.
#     The boolean translates to greater (True) or lesser than (False) the limit. Part of the servo section.
#
#     Parameters
#     ----------
#     deviceNumber : :obj:`int`
#         :obj:`ServoDevice.deviceNumber`
#     servo : :obj:`int`
#         Servo index :obj:`servo.channel`
#
#     Returns
#     -------
#     :obj:`bool`
#         The snap condition as a boolean.
#
#     """
#     servo = device(deviceNumber).servo(servo)
#     return servo.snapGreater


def getLockRange(deviceNumber, servo):
    """Returns a list containing minimum and maximum value of the autolock sections RangeSlider.abs

    The AutoLock options are located in the servo section.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servo : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    obj:`list`
        [min, max]

    """
    servo = device(deviceNumber).servo(servo)
    return [servo._autolock['min'], servo._autolock['max']]


def getLockThreshold(deviceNumber, servo):
    """Returns the threshold value of the autolock.

    The AutoLock options are located in the servo section.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servo : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    obj:`float`
        The voltage value.

    """
    servo = device(deviceNumber).servo(servo)
    return servo._autolock['threshold']


def getLockGreater(deviceNumber, servo):
    """Return the initial value of the lock condition of a servo.
    The boolean translates to greater (True) or lesser than (False) the threshold.
    Part of the servo section.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servo : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`bool`
        The lock condition as a boolean.

    """
    servo = device(deviceNumber).servo(servo)
    return servo._autolock['greater']


def getAutolockList(deviceNumber):
    """Returns a list containing the channel indices of all active
    servo locks for the AutoLock checklist.

    The AutoLock checklist is part of the app header.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    obj:`list`
        List containing servo channel indices.

    """
    locks = []
    for i in range(1, settings.NUMBER_OF_SERVOS + 1):
        state = device(deviceNumber).servo(i)._autolock['state']
        if state:
            locks.append(i)
    return locks


def getLockRelock(deviceNumber, servo):
    """Return whether auto-relock is on or off for a given servo.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servo : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`list`
        Empty list means `False`, element in list means `True`.

    """
    result = []
    if device(deviceNumber).servo(servo).relock:
        result.append('on')
    return result


def getLockStatus(deviceNumber, servo):
    servo = device(deviceNumber).servo(servo)
    lockstatus = servo.lockState
    greater = servo.lockGreater
    if greater:
        greater = '>'
    else:
        greater = '<'
    min, max = servo.lockSearchMin, servo.lockSearchMax
    threshold = servo.lockThreshold
    return 'Autolock: {} | {}{} | [{} → {}]'.format(lockstatus, greater, threshold, min, max)
#
#
#
# INTERFACE FUNCTIONALITY
# These methods handle communication of device and interface.
# They are associated with callbacks.
#
#
#


def callServoName(deviceNumber, servoNumber, submit, name):
    """Apply the name specified in the servo section's name input
    to the targeted :obj:`servo.name` and return the name string to update the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    submit : :obj:`int`
        Number of times the input's submit event occured (pressing Enter while in input).
        None on startup.
    name : :obj:`String`
        Name for the :obj:`servo` and the UI's servo section.

    Returns
    -------
    :obj:`String`
        :obj:`servo.name`
    """
    if submit is None:
        raise PreventUpdate()
    servo = device(deviceNumber).servo(servoNumber)
    servo.name = name
    return servo.name


def callInputSensitivity(selected, deviceNumber, servoNumber):
    """Apply the input sensitivity as specified by the dropdown
    of the servo section's input options to :obj:`servo.inputSensitivity`
    and return information as a string to update UI.

    Parameters
    ----------
    selected : :obj:`int`
        One of the dropdown options. The mode is specified with ints from `0` to `3`.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`String`
        Information formatted for the `html.P()` above the dropdown.
    """
    servo = device(deviceNumber).servo(servoNumber)
    servo.inputSensitivity = selected
    limits = [10, 5, 2.5, 1.25]
    return f'Input sensitivity (Limit: {limits[selected]}V, Mode: {selected})'


def callAuxSensitivity(selected, deviceNumber, servoNumber):
    """Apply the aux sensitivity as specified by the dropdown
    of the servo section's output options to :obj:`servo.auxSensitivity`
    and return information as a string to update UI.

    Parameters
    ----------
    selected : :obj:`String`
        One of the dropdown options. The mode is specified with ints from `0` to `3`.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`String`
        Information formatted for the `html.P()` above the dropdown.

    """
    servo = device(deviceNumber).servo(servoNumber)
    servo.auxSensitivity = selected
    limits = [10, 5, 2.5, 1.25]
    return f'Aux sensitivity (Limit: {limits[selected]}V, Mode: {selected})'


def callReboot(clicks, deviceNumber):
    """Reboot the ADwin device.

    Return a :obj:`String` with information on reboot.
    Return `None` if button hasn't been pressed
    (to accound for Dash callbacks firing on start-up).

    Parameters
    ----------
    clicks : :obj:`int`
        Description of parameter `clicks`.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`String`
        Information on the reboot process for the UI.

    """
    if clicks is not None:
        try:
            dev = device(deviceNumber)
            dev.reboot()
            return 'Rebooted successfully.'
        except ADwinError:
            return 'Reboot encountered an error.'
    else:
        return None


def callSave(clicks, filename, deviceNumber):
    """Save the :obj:`nqontrol.ServoDevice` to the
    "./src"-directory using the filename provided.

    If no filename was provided saves a 'default'.

    Parameters
    ----------
    clicks : :obj:`int`
        Description of parameter `clicks`.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    filename : :obj:`String`
        Specify a `String` as the potential filename. If not provided, save to 'default'.

    Returns
    -------
    :obj:`String`
        Text info on save process. None on start-up.

    Raises
    -------
    ExceptionName
        Why the exception is raised.

    """
    if (clicks is not None) and (clicks > 0):
        try:
            if filename is None:
                filename = 'default'
            dev = device(deviceNumber)
            dev.saveDeviceToJson(filename)
            log.info(f'Saved device as JSON in: {filename}')
            return f'Saved as {filename}'
        except Exception as e:
            log.warning(e)
            raise PreventUpdate()
    # return None only on start-up, when the button has not been clicked.
    return None


def callMonitorUpdate(deviceNumber, servoNumber, visibleChannels):
    """Handle live plotting functionality for the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    visibleChannels : :obj:`list`
        List of Strings specifying the signals to be shown, arbitrary choice of:
        ['input', 'aux', 'output'].

    Returns
    -------
    :obj:`plotly.graph_objs`
        Returns a plotly/Dash graph_object/figure, consisting of data and layout.
        See https://plot.ly/ for detailed info.

    """
    # a device has to be connected and only returns an updating figure
    # if channels are set to active via the Checklist element below the Graph UI
    if DEVICES and visibleChannels:
        servo = device(deviceNumber).servo(servoNumber)
        # this should never happen anyway
        # if servo.fifoStepsize is None:
        #     servo.fifoStepsize = 10

        # Setting visible channels
        servo.realtime['ydata'] = visibleChannels
        # Would be a list containing at least one of the keywords used in `colors` below
        df = servo._prepareData()
        # this will be a list of plotly.graph_objs
        traces = []
        # Assigning colors for specific channel tags, if not set manually,
        # colors are assigned by plotly but incosistently, depending on order of adding plots.
        colors = {
            'input': '#1f77b4',
            'aux': '#ff7f0e',
            'output': '#2ca02c'
        }
        for label in visibleChannels:
            data = df[label]
            # For more options on styling the graphs, please look at the plotly documentation
            traces.append(go.Scattergl(x=df.index, y=data, name=label, mode='lines',
                                       marker=dict(color=colors[label])))
        figure = {
            'data': traces,
            'layout': go.Layout(yaxis=dict(title='Amplitude (V)'))
        }
        return figure
    else:
        raise PreventUpdate()


def callMonitorUpdateChannels(deviceNumber, servoNumber, visibleChannels):
    """Set visible channels attribute of :obj:`servo.realtime`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    visibleChannels : :obj:`list`
        List of Strings specifying the signals to be shown, arbitrary choice of:
        ['input', 'aux', 'output'].

    Returns
    -------
    :obj:`String`
        Feedback string on what was applied. Just for UI purposes.

    """
    if DEVICES and visibleChannels:
        servo = device(deviceNumber).servo(servoNumber)
        servo.realtime['ydata'] = visibleChannels
        return 'ydata set to' + str(visibleChannels)
    else:
        return 'Empty channels'


def callWorkloadTimestamp(deviceNumber):
    """Handle callback for Workload and Timestamp output in the UIs header section.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`String`
        The workload and timestamp in a String description.

    """
    try:
        return f'Workload: {device(deviceNumber).workload}'\
               f'Timestamp: {device(deviceNumber).timestamp}'
    except ADwinError:
        return 'Workload: ERR Timestamp: ERR'


def callOffset(deviceNumber, servoNumber, offset):
    """Handle the servo offset input callback for the UI's servo input section.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    offset : :obj:`String`
        String from the input field.

    Returns
    -------
    :obj:`String`
        The offset embedded in a string for the html.P label.

    """
    servo = device(deviceNumber).servo(servoNumber)
    try:
        offset = fast_real(offset, raise_on_invalid=True)
    except (ValueError, TypeError):
        raise PreventUpdate('Empty or no real number input.')
    # Please note that servo checks for correct value.
    if servo.offset != offset:
        servo.offset = offset
    return 'Offset (' + str(servo.offset) + 'V)'


def callGain(context, deviceNumber, servoNumber, gain):
    """Handle the servo gain input callback for the UI's servo input section.

    Parameters
    ----------
    context : :obj:'json'
        Dash callback context. Please check the dash docs for more info.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    gain : :obj: `String`
        String from the input field.

    Returns
    -------
    :obj:`String`
        The gain embedded in a string for the html.P label.

    """
    servo = device(deviceNumber).servo(servoNumber)

    # determining context of input
    triggered = context.triggered[0]['prop_id'].split('.')[0]

    if 'gain' in triggered:
        # case when gain is changed by submitting the input with Enter
        try:
            gain = fast_real(gain, raise_on_invalid=True)
        except (ValueError, TypeError):
            raise PreventUpdate('Empty or no real number input.')
        if servo.gain != gain:
            servo.gain = gain

    return 'Gain (' + str(servo.gain) + ')'


def callServoDesignGain(gain, deviceNumber):
    """Handle the dummy ServoDesign gain callback for the UI.
    The :obj:`ServoDesign` is associated with the :obj:`nqontrol.ServoDevice`
    and can then be applied to a :obj:`servo`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    gain: :obj:`String`
        String from the input field.

    Returns
    -------
    :obj:`String`
        The gain embedded in a string for the html.P label.

    """
    try:
        gain = fast_real(gain, raise_on_invalid=True)
    except (ValueError, TypeError):
        raise PreventUpdate('Empty or no real number input.')
    # The
    servoDesign = device(deviceNumber).servoDesign
    if servoDesign.gain != gain:
        servoDesign.gain = gain
    return 'Gain (' + str(servoDesign.gain) + ')'


def callServoChannels(deviceNumber, servoNumber, inputValues):
    """Handle the checklists for both the input and output section of servo controls.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    inputValues : :obj:`list`
        List for either input or output section.
        Labels for input section are 'input', 'offset'.
        For output section 'aux' and 'output'.

    Returns
    -------
    type
        Description of returned object.

    """
    servo = device(deviceNumber).servo(servoNumber)
    if 'input' in inputValues:
        servo.inputSw = True
    else:
        servo.inputSw = False

    if 'offset' in inputValues:
        servo.offsetSw = True
    else:
        servo.offsetSw = False

    if 'aux' in inputValues:
        servo.auxSw = True
    else:
        servo.auxSw = False

    # if 'snap' in inputValues:
    #     servo.snapSw = True
    # else:
    #     servo.snapSw = False

    if 'output' in inputValues:
        servo.outputSw = True
    else:
        servo.outputSw = False

    return ''


def callApplyServoDesign(servoNumber, deviceNumber, n_clicks):
    """Callback for the 'Apply'-Button in the Second Order Section of the UI.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    n_clicks : :obj:`int`
        Integer indicating times the Button has been clicked.
        Used to prevent callback from firing on start-up.

    Returns
    -------
    :obj:`String`
        String description to pass on to UI label.

    """
    if n_clicks is not None:
        dev = device(deviceNumber)
        servoDesign = dev.servoDesign
        servo = dev.servo(servoNumber)
        servo.applyServoDesign(servoDesign)
        return f'Applied ServoDesign on {servoNumber}.'
    raise PreventUpdate()


def callApplyFilterLabels(applyNumber, servoNumber, deviceNumber, n_clicks):
    """Handle updating filter labels in the servo control section
    when 'Apply' button is pressed for the Second Order Section.

    Due to the callback mechanic, an additional parameter `applyNumber` has to be passed,
    to ensure the labels are only updated in the corresponding section.

    Parameters
    ----------
    applyNumber : :obj:`int`
        Parameter compared to the `servoNumber`.
        Only fires if they are the same.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    n_clicks : :obj:`int`
        Indicates times the button has been clicked.
        Used to prevent callback execution on start-up.

    Returns
    -------
    :obj:`list`
        List containing the new labels of the checklist UI element.
        Each label is defined as {`label`: xxx, `value`: xxx}.
        The value will always correspond to the filter index.

    """
    if (applyNumber == servoNumber) and (n_clicks is not None):
        servoDesign = device(deviceNumber).servoDesign
        labels = []
        for i in range(servoDesign.MAX_FILTERS):
            filter = servoDesign.get(i)
            if filter is not None:
                labels.append(filter.description)
            else:
                labels.append('Filter {}'.format(i))
        return [{'label': labels[i], 'value': i} for i in range(servoDesign.MAX_FILTERS)]
    else:
        raise PreventUpdate()


def callApplyFilterValues(applyNumber, servoNumber, deviceNumber, n_clicks):
    """Handle updating filter checklist values in the servo control section
    when 'Apply' button is pressed for the Second Order Section.

    Due to the callback mechanic, an additional parameter `applyNumber` has to be passed,
    to ensure the checklist values are only updated in the corresponding section.

    Parameters
    ----------
    applyNumber : :obj:`int`
        Parameter compared to the `servoNumber`. Only fires if they are the same.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    n_clicks : :obj:`int`
        Indicates times the button has been clicked. Used to prevent callback execution on start-up.

    Returns
    -------
    :obj:`list`
        List containing the values of all active filters for checklist UI element.
        The value corresponding to each filter is its respective index.

    """
    if (applyNumber == servoNumber) and (n_clicks is not None):
        servoDesign = device(deviceNumber).servoDesign
        values = []
        for i in range(servoDesign.MAX_FILTERS):
            filter = servoDesign.get(i)
            if filter is not None and filter.enabled:
                values.append(i)
        return values
    else:
        raise PreventUpdate()


def callToggleServoFilters(deviceNumber, servoNumber, values):
    """Handle callback of the filter checklist in the servo section of the UI.
    Passes a list of active filters to the :obj:`servo`.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`
    values : :obj:`list`
        List containing the indices of active filters.

    Returns
    -------
    :obj:`String`
        Just an empty string since UI callback needs an output.

    """
    servoDesign = device(deviceNumber).servo(servoNumber).servoDesign
    for i in range(servoDesign.MAX_FILTERS):
        f = servoDesign.get(i)
        if f is not None:
            if i in values:
                f.enabled = True
            else:
                f.enabled = False
    device(deviceNumber).servo(servoNumber).applyServoDesign()
    return ''


def callPlantParse(deviceNumber, filename, contents, n_clicks, timestamp, timestamp_old):
    """Handle parsing of uploaded plant for :obj:`ServoDesign` of the Second Order Section.
    Also handles 'unplanting'.
    Has to be handled by one function as both callbacks would target the same output container.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    filename : :obj:`String`
        Name of the input file. Dash does not send the full path.
    contents : :obj:`String`
        Base64 encoded string of the file contents.
    n_clicks : :obj:`int`
        Number of times the 'Unplant' button has been clicked

    Returns
    -------
    :obj:`String`
        Timestamp of the last time the button was clicked.

    """
    if n_clicks is None and contents is None:
        raise PreventUpdate()
    servoDesign = device(deviceNumber).servoDesign
    # first check if the callback has been fired by the unplant button
    if timestamp_old != timestamp:
        servoDesign.plant = None
    elif contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8', 'ignore')
        try:
            df = io.reads(decoded)
            servoDesign.plant = df
        except Exception as e:
            log.warn(e)
            raise PreventUpdate(str(e))
    return timestamp


def callPlotServoDesign(deviceNumber):
    """Handle plotting of amplitude and phase of the ServoDesign
    associated with the device over frequency.
    Part of the UI's Second Order Section.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`plotly.graph_objs`
        Returns a plotly/Dash graph_object/figure, consisting of data and layout.
        See https://plot.ly/ for detailed info.

    """
    fig = subplots.make_subplots(rows=2, cols=1, shared_xaxes=True,
                                 subplot_titles=('Amplitude', 'Phase'), print_grid=False)
    servoDesign = device(deviceNumber).servoDesign
    fig.update_xaxes(exponentformat="e", tick0=0, tickmode="linear", dtick=1)
    fig.update_xaxes(type="log")
    fig['layout']['yaxis1'].update(title='Amplitude (dB)')
    fig['layout']['yaxis2'].update(title='Phase (Hz)')
    fig['layout'].update(title='Transfer Function')
    fig['layout'].update(showlegend=False)
    # return an empty figure if no filters exist in ServoDesign - needed to make plot appear empty.
    # Preventing the update would keep the previous figure.
    if len(servoDesign) == 0:
        fig.add_trace(go.Scattergl(x=[0], y=[-1]), 1, 1)
        fig.add_trace(go.Scattergl(x=[0], y=[-1]), 2, 1)
        fig['layout'].update(height=800)
        return fig
    else:
        df = servoDesign.plot(plot=False)
        fig.add_trace(go.Scattergl(x=df.index, y=df['Servo A']), 1, 1)
        fig.add_trace(go.Scattergl(x=df.index, y=df['Servo P']), 2, 1)
        if 'Servo+TF A' in df:
            fig.add_trace(go.Scattergl(x=df.index, y=df['Servo+TF A']), 1, 1)
            fig.add_trace(go.Scattergl(x=df.index, y=df['Servo+TF P']), 2, 1)
        return fig


def callFilterDescription(dropdown, main, sec, deviceNumber, filterIndex):
    """Updates the filter description labels in the Second Order Section of the UI
    when the dropdown selection (filter type) changes.

    Parameters
    ----------
    dropdown : :obj:`String`
        Value passed by the dropdown. Filter type as a string.
    main : :obj:`String`
        Main filter parameter. Contents of the UI input as a string. None if empy.
    sec : :obj:`String`
        Secondary filter parameter. Contentes of the UI input as a string. None if empy.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    filterIndex : :obj:`int`
        Index of the filter in the :obj:`ServoDesign`.

    Returns
    -------
    :obj:`String`
        The description string if a filter type is selected or None.

    """
    if dropdown is not None:

        for subclass in Filter.__subclasses__():
            if subclass.__name__ == dropdown:
                if not main:
                    return str(subclass(1, 1).description_long)
                else:
                    try:
                        main = fast_real(main, raise_on_invalid=True)
                        # Checking for secInput
                        if sec:
                            try:
                                sec = fast_real(sec, raise_on_invalid=True)
                                return str(subclass(main, sec).description)
                            except (ValueError, TypeError):
                                return str(subclass(main).description)
                        else:
                            return str(subclass(main).description)
                    except (ValueError, TypeError):
                        return str(subclass(1, 1).description_long)
    else:
        return None


def _handleFilter(dropdown, main, sec, active, deviceNumber, filterIndex):
    # Determining filter type
    for subclass in Filter.__subclasses__():
        if subclass.__name__ == dropdown:
            filter = subclass
    servoDesign = device(deviceNumber).servoDesign
    if main:
        try:
            main = fast_real(main, raise_on_invalid=True)
        except (ValueError, TypeError) as e:
            log.info(e)
            raise PreventUpdate('No real number input in secondary field.')
    else:
        raise PreventUpdate('No main parameter.')
    if sec:
        try:
            sec = fast_real(sec, raise_on_invalid=True)
            # only add filter with second parameter if sec was set,
            # since the filters have different default values for the secondary parameter
            # and shouldnt be overwritten with None
            servoDesign.add(filter(main, sec, enabled=bool(active)), index=filterIndex)
        except (ValueError, TypeError) as e:
            log.info(e)
            raise PreventUpdate('No real number input in main field.')
    else:
        # add filter with main and secondary value
        servoDesign.add(filter(main, enabled=bool(active)), index=filterIndex)


def callFilterField(dropdown, main, sec, active, deviceNumber, filterIndex):
    """Handle input changes for both the main and secondary parameter fields of filters in the
    Second Order Section of the UI.
    Applies the changes to :obj:`ServoDevice.servoDesign` accordingly.

    Parameters
    ----------
    dropdown : :obj:`String`
        Value passed by the dropdown. Filter type as a string.
    main : :obj:`String`
        Main filter parameter. Contents of the UI input as a string. None if empy.
    sec : :obj:`String`
        Secondary filter parameter. Contentes of the UI input as a string. None if empy.
    active : :obj:`list`
        List indicating whether a checkbox is enabled for the filter or not.
        If active contains the filter index, empty if inactive.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    filterIndex : :obj:`int`
        Index of the filter in the :obj:`ServoDesign`.

    Returns
    -------
    :obj:`String`
        Datetime string to pass to output. The output triggers a callback chain as well.

    """
    servoDesign = device(deviceNumber).servoDesign
    if dropdown is not None:
        _handleFilter(dropdown, main, sec, active, deviceNumber, filterIndex)
    else:
        servoDesign.remove(filterIndex)
    return str(datetime.time())


def callFilterVisible(dropdownInput):
    """Handle visibility of filter input fields and description depending on
    whether a value is selected in the dropdown. Refers to the Second Order Section of the UI.

    Parameters
    ----------
    dropdownInput : :obj:`String`
        Either filter type as a string or `None`.

    Returns
    -------
    :obj:`Dictionary`
        Dictionary containing CSS style information for Dash.
        Changes 'display' style of filter inputs to either 'none' or 'inline-block'.

    """
    if dropdownInput is not None:
        return {'display': 'inline-block'}
    else:
        return {'display': 'none'}


def getFilterOptions():
    """Return all possible filter types defined by the :obj:`ServoDesign` library of `openqlab`.
    Used to automate UI lists of possible filter types.

    Returns
    -------
    :obj:`list`
        List containing all possible filter types as Strings.

    """
    return [filter for filter in Filter.__subclasses__()]


def callToggleRamp(targetInput, deviceNumber):
    """Set the ramp of ADwin to one of the possible channels.

    Parameters
    ----------
    targetInput : :obj:`int`
        Target servo channel. `False` if set to Off in the UI,
        as the servo defines the state that way.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`String`
        Information string as callback needs some output. Basically a dummy.

    """
    servo = device(deviceNumber).servo(targetInput)
    if not targetInput:
        device(deviceNumber).servo(1).disableRamp()
        return 'Disabled'
    elif servo._autolock['state']:
        log.warn('Autolock is active, ramp was not activated.')
        return 'Could not update ramp. lock was active.'
    else:
        if not servo.rampEnabled:
            servo.enableRamp()
        return 'Ramp on channel ' + str(targetInput)


def callAutolock(values, deviceNumber):
    """Enables the auto-lock feature on all selected servos.
    Ramp is not compatible with Autolock (Essentially, the autolock should be a better ramp).

    GUI wise, the autolock-checklist is located in the header section.

    Parameters
    ----------
    values : :obj:`list`
        The GUI returns a list containing all channel numbers where the autolock should be active.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`bool`
        Returns False in order to disable Ramp in the GUI in case there is an active autolock.

    """
    # check whether list is empty
    ramp = device(deviceNumber).rampEnabled
    for i in range(1, settings.NUMBER_OF_SERVOS + 1):
        servo = device(deviceNumber).servo(i)
        if i in values:
            # in order to retrigger a lock one has to uncheck the box first and recheck it
            # only set this to 1 if it was 0 before (inactive before)
            if not servo._autolock['state']:
                servo.autolock(1)  # setting state to 1 starts searching for peak
            if ramp == i:
                # setting the ramp to 0 for the GUI in case RAMP was active on an autolock channel
                ramp = 0
        else:
            servo.autolock(0)  # setting state to zero turns off the lock
        servo._readFilterControl()
    # returning the ramp value for the GUI,
    # if the ramp doesnt interfere with any lock, nothing changes
    return ramp


# def lockStatus(lockstate, threshold, sliderlist, greater, context, deviceNumber, servo):
#     servo = device(deviceNumber).servo(servo)
#
#     # determining context of input
#     triggered = context.triggered[0]['prop_id'].split('.')[0]
#
#     # checking for input changes, sending to servo accordingly
#     if 'lockSlider' in triggered and sliderlist:
#         servo.lockSearchMin = sliderlist[0]
#         servo.lockSearchMax = sliderlist[1]
#
#     if 'threshold' in triggered:
#         try:
#             threshold = fast_real(threshold, raise_on_invalid=True)
#         except (ValueError, TypeError):
#             raise PreventUpdate('Empty or no real number input.')
#         if -10 >= threshold >= 10:
#             log.warn('Value out of bounds!')
#             raise PreventUpdate('Value has to be between -10 and 10V!!')
#         servo.lockThreshold = threshold
#
#     if 'lockGreater' in triggered:
#         if not isinstance(greater, bool):
#             raise PreventUpdate('Has to be a boolean.')
#         servo.lockGreater = greater
#
#     # getting all values, sending to GUI
#     lockstatus = servo.lockState
#     greater = servo.lockGreater
#     if greater:
#         greater = '>'
#     else:
#         greater = '<'
#     min, max = servo.lockSearchMin, servo.lockSearchMax
#     threshold = servo.lockThreshold
#     auto = servo.relock
#     if auto:
#         auto = '(relock)'
#     else:
#         auto = ''
#     return 'Autolock: {} | {}{} | [{} → {}] | {}'.format(
#            lockstatus, greater, threshold, min, max, auto)


# def callAutolockRelock(values, deviceNumber, servo):
#     """Set whether the AutoLock should relock automatically whenever falling
#     above/below threshold for a given servo.
#
#     Parameters
#     ----------
#     values : :obj:`list`
#         As with all Dash checklists, even though this is for a single element,
#         the callback input is a list. Empty list means off, none-empty means on.
#     deviceNumber : :obj:`int`
#         :obj:`ServoDevice.deviceNumber`
#     servoNumber : :obj:`int`
#         Servo index :obj:`servo.channel`
#
#     Returns
#     -------
#     :obj:`bool`
#         The relock value, since the UI requires a return.
#
#     """
#     servo = device(deviceNumber).servo(servo)
#     if values:
#         servo.relock = True
#     else:
#         servo.relock = False
#     return servo.relock


def callRamp(amp, freq, context, deviceNumber, servoNumber):
    """Send ramp parameters entered in servo control section of the UI to
    the corresponding :obj:`nqontrol.Servo`.

    Parameters
    ----------
    amp : :obj:`float`
        Ramp amplitude.
    freq : :obj:`float`
        Ramp frequency.
    context : :obj:'json'
        Dash callback context. Please check the dash docs for more info.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`
    servoNumber : :obj:`int`
        Servo index :obj:`servo.channel`

    Returns
    -------
    :obj:`String`
        UI label string describing current ramp state.

    """
    servo = device(deviceNumber).servo(servoNumber)

    triggered = context.triggered[0]['prop_id'].split('.')[0]
    if 'ramp' in triggered:
        servo.rampAmplitude = amp
    if 'freq' in triggered:
        servo.rampFrequency = freq
    amp = servo.rampAmplitude
    freq = servo.rampFrequency
    return 'Amplitude: {} | Frequency: {}'.format(amp, round(freq, 2))


def callADwinMonitor(channel, servo, card, deviceNumber):
    """Set a ADwin hardware monitor channel.

    Parameters
    ----------
    channel : :obj:`int`
        ADwin hardware monitor channel index.
    servo : :obj:`int`
        Servo channel index.
    card : :obj:`String`
        String specify which servo signal to monitor. One of 'input', 'aux', 'output' or 'ttl'.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`list`
        Summary list with all the parameters that have been passed.
        Mostly used because the callback requires some output.

    """
    if servo is None or card is None:
        raise PreventUpdate()
    dev = device(deviceNumber)
    dev.enableMonitor(channel, servo, card)
    return [channel, servo, card]


def callTempVoltageLimit(submit, value, servo, deviceNumber):
    """Set voltage limit of a servos temperature control.

    Parameters
    ----------
    submit : :obj:`int`
        Times the user actively submitted the input.
    value : :obj:`String`
        The voltage limit. Might have to be converted to a float.
        Input field usually passes Strings though.
    servo : :obj:`int`
        Servo channel index.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`tuple`
        Tuple containing target servo index and value.

    """
    if submit is None:
        raise PreventUpdate()
    tempFeedback = device(deviceNumber).servo(servo).tempFeedback
    try:
        value = fast_real(value, raise_on_invalid=True)
    except (ValueError, TypeError):
        raise PreventUpdate('Empty or no real number input.')
    if tempFeedback is not None:
        tempFeedback.voltage_limit = value
    else:
        raise PreventUpdate('No temperature feedback active yet. Use Start button.')
    return (servo, value)  # returns a tuple to store as information


def callTempInterval(submit, value, servo, deviceNumber):
    """Set update interval of a servos temperature control.

    Parameters
    ----------
    submit : :obj:`int`
        Times the user actively submitted the input.
    value : :obj:`String`
        The update interval. Might have to be converted to a float.
        Input field usually passes Strings though.
    servo : :obj:`int`
        Servo channel index.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`tuple`
        Tuple containing target servo index and value.

    """
    if submit is None:
        raise PreventUpdate()
    tempFeedback = device(deviceNumber).servo(servo).tempFeedback
    try:
        value = fast_real(value, raise_on_invalid=True)
    except (ValueError, TypeError):
        raise PreventUpdate('Empty or no real number input.')
    if tempFeedback is not None:
        tempFeedback.update_interval = value
    else:
        raise PreventUpdate('No temperature feedback active yet. Use Start button.')
    return (servo, value)  # returns a tuple to store as information


def callTempMtd(numSubmit, portSubmit, num, port, servo, deviceNumber):
    """Send mtd settings as a tuple to temperature control of a servo.

    Parameters
    ----------
    numSubmit : :obj:`int`
        Times the user actively submitted the mtdnum input.
    portSubmit : :obj:`int`
        Times the user actively submitted the mtdport input.
    num : :obj:`String`
        The mtd number. Might have to be converted to int.
        Input field usually passes Strings though.
    port : :obj:`String`
        The mtd port. Might have to be converted to int. Input field usually passes Strings though.
    servo : :obj:`int`
        Servo channel index.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`tuple`
        Tuple containing target servo index, port and num.

    """
    if numSubmit is None and portSubmit is None:
        raise PreventUpdate()
    tempFeedback = device(deviceNumber).servo(servo).tempFeedback
    try:
        num = fast_int(num, raise_on_invalid=True)
        port = fast_int(port, raise_on_invalid=True)
    except (ValueError, TypeError):
        raise PreventUpdate('Empty or no real number input.')
    if tempFeedback is not None:
        tempFeedback.mtd = (port, num)
    else:
        raise PreventUpdate('No temperature feedback active yet. Use Start button.')
    return (servo, port, num)  # returns a tuple to store as information


def callTempDt(submit, value, servo, deviceNumber):
    """Set dT of a servos temperature control.

    Parameters
    ----------
    submit : :obj:`int`
        Times the user actively submitted the input.
    value : :obj:`String`
        dT value. Might have to be converted to a float. Input field usually passes Strings though.
    servo : :obj:`int`
        Servo channel index.
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`tuple`
        Tuple containing target servo index and value.

    """
    if submit is None:
        raise PreventUpdate()
    tempFeedback = device(deviceNumber).servo(servo).tempFeedback
    try:
        value = fast_real(value, raise_on_invalid=True)
    except (ValueError, TypeError):
        raise PreventUpdate('Empty or no real number input.')
    if tempFeedback is not None:
        tempFeedback.dT = value
    else:
        raise PreventUpdate('No temperature feedback active yet. Use Start button.')
    return (servo, value)  # returns a tuple to store as information


def callTempButton(clicks, dt, num, port, interval, voltLim, servo, deviceNumber):
    """Short summary.

    Parameters
    ----------
    clicks : type
        Description of parameter `clicks`.
    dt : type
        Description of parameter `dt`.
    num : type
        Description of parameter `num`.
    port : type
        Description of parameter `port`.
    interval : type
        Description of parameter `interval`.
    voltLim : type
        Description of parameter `voltLim`.
    servo : type
        Description of parameter `servo`.
    deviceNumber : type
        Description of parameter `deviceNumber`.

    Returns
    -------
    type
        Description of returned object.

    """
    if clicks is None:
        raise PreventUpdate()
    channel = servo
    servo = device(deviceNumber).servo(servo)
    mod = clicks % 2
    if mod == 1:  # start case
        try:
            dt = fast_real(dt, raise_on_invalid=True)
            num = fast_int(num, raise_on_invalid=True)
            port = fast_int(port, raise_on_invalid=True)
        except (ValueError, TypeError) as e:
            log.warning(e)
            raise PreventUpdate('The dT and mtd fields must be specified correctly.')

        try:
            interval = fast_real(interval, raise_on_invalid=True)
        except (ValueError, TypeError):
            interval = None
        try:
            voltLim = fast_real(voltLim, raise_on_invalid=True)
        except (ValueError, TypeError):
            voltLim = None

        mtd = (port, num)
        if interval is None and voltLim is None:
            servo.tempFeedbackStart(dT=dt, mtd=mtd)
        elif interval is None:
            servo.tempFeedbackStart(dT=dt, mtd=mtd, voltage_limit=voltLim)
        elif voltLim is None:
            servo.tempFeedbackStart(dT=dt, mtd=mtd, update_interval=interval)
        else:
            servo.tempFeedbackStart(dT=dt, mtd=mtd, voltage_limit=voltLim, update_interval=interval)

        log.info(f'Started temperature control on servo {channel} '\
                 'with parameters dt {dt}, mtd {mtd}, interval {interval} and limit {voltLim}')

        return 'Stop'  # new label text for the button
    elif mod == 0:  # stop case
        if servo.tempFeedback is not None:
            servo.tempFeedbackStop()
        return 'Start'  # new label text for the button


# def callSnapParam(limit, greater, servo, deviceNumber):
#     """Set the snapping parameters for the servo.
#
#     Parameters
#     ----------
#     limit : :obj:`float`
#         Voltage limit for snapping.
#     greater : :obj:`bool`
#         Boolean specifying whether to snap when greater than or lower than limit.
#     deviceNumber: :obj:`int`
#         :obj:`ServoDevice.deviceNumber`
#     servo: :obj:`int`
#         Servo index :obj:`servo.channel`
#
#     Returns
#     -------
#     :obj:`String`
#         Updates the snap label with the current limit value.
#
#     """
#     servo = device(deviceNumber).servo(servo)
#     try:
#         limit = fast_real(limit, raise_on_invalid=True)
#     except (ValueError, TypeError):
#         raise PreventUpdate('A snap value has to be provided.')
#     servo.snap = limit
#     servo.snapGreater = greater
#     servo.snapSend(limit, greater)
#     return f'Snap ({limit} V)'
#
#
#
# Class methods
#
#
#


def device(deviceNumber):
    """Return the device with given number.

    Parameters
    ----------
    deviceNumber : :obj:`int`
        :obj:`ServoDevice.deviceNumber`

    Returns
    -------
    :obj:`nqontrol.ServoDevice`
        A ServoDevice object.

    """
    if DEVICES[deviceNumber - 1] is not None:
        return DEVICES[deviceNumber - 1]
    else:
        raise Exception("Can not give you a device that does not exist!")
