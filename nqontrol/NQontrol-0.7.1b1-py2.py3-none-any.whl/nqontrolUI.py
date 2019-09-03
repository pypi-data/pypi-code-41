"""NQontrol UI class"""
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------
# Run file in cmd. App runs on http://127.0.0.1:8050/.
# Server adress is given in cmd window.
# For documentation please read the comments. For information about Dash and Plotly go to:
#
# https://dash.plot.ly/
# ----------------------------------------------------------------------------------------
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_daq import ToggleSwitch
from dash.dependencies import Input, Output, State
from abc import ABCMeta, abstractmethod
from nqontrol import settings, controller


class UI:
    """Short summary.

    Parameters
    ----------
    app: :obj:`dash.Dash`
        The app object.

    Attributes
    ----------
    _devicesList : type
        Description of attribute `_devicesList`.
    _app : type
        Description of attribute `_app`.
    __setUpComponents : type
        Description of attribute `__setUpComponents`.
    layout : type
        Description of attribute `layout`.
    __setCallbacks : type
        Description of attribute `__setCallbacks`.

    """

    def __init__(self, app):
        self._devicesList = settings.DEVICES_LIST
        self._app = app
        self._setUpComponents()

    @property
    def layout(self):
        """Return the app structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        layouts = []
        for uiDevice in self._uiDevices:
            layouts = layouts + uiDevice.layout
        return html.Div(children=layouts, className='container-fluid')

    def _setUpComponents(self):
        self._uiDevices = [UIDevice(self._app, deviceNumber) for deviceNumber in self._devicesList]

    def setCallbacks(self):
        for uiDevice in self._uiDevices:
            uiDevice.setCallbacks()


class UIComponent:
    """Abstract class of UI components. In order to organize the Dash system and make features more modular, object structures are used for complex subsections of the interface. Every component takes the app object running the server as default parameter. Callback functions and handles all user interaction to the backend are defined in the :obj:`controller` module. Callbacks are performed by the app (which is a Flask server that gets passed to gunicorn).
    Components also implement two default class functions/properties: `layout`, which returns the HTML layout in Dash syntax (sometimes, the layout has to be handled as part of initialization, when the layout needs more syntactic functionality), and `setCallbacks()``, which initializes all callbacks in startup. Dash usually requires the layout to be defined before the callbacks, as such, all calls to layout have to be made first. The `nqontrolUI` class starts a chain of calls to `setCallbacks()`, the majority of which are set in the `UIDevice` class.

    Parameters
    ----------
    app : dash.Dash
        The dash app. For more information visit https://dash.plot.ly/.
    deviceNumber : Integer
        Device index of `servoDevice` object.

    Attributes
    ----------
    _app : type
        Description of attribute `_app`.
    _deviceNumber : Integer
        Device index of `servoDevice` object.

    """
    __metaclass__ = ABCMeta

    def __init__(self, app, deviceNumber):
        self._app = app
        self._deviceNumber = deviceNumber

    @property
    @abstractmethod
    def layout(self):
        pass

    @abstractmethod
    def setCallbacks(self):
        pass


class UIDevice(UIComponent):
    """Main frame of the Interface, each device gets one (currently only supports a single device, though). Implements a few top level elements of the UI, initializes and arranges all subsections.

    The layout is constructed as follows:

    **UIDevice** (see :obj:`nqontrol.settings.DEVICES_LIST`) _(header, servoDetails and rest refer to local variables within the layout property for better source code navigation)_
        header (defined within UIDevice, see layout property)
        servoDetails (as many as defined in :obj:`settings.NUMBER_OF_SERVOS`, defined within UIDevice, see layout property)
            :obj:`nqontrol.nqontrolUI.UIServoSection`
            :obj:`nqontrol.nqontrolUI.UIRamp`
            Servo Naming element (defined within UIDevice)
        rest
            :obj:`nqontrol.nqontrolUI.UIServoDesignPlot`
                :obj:`nqontrol.nqontrolUI.UISecondOrderSection`
                    Plant section, servo target, upload field, apply/unplant buttons
                    :obj:`nqontrol.nqontrolUI.UIFilter` (as many as defined for default ServoDesign filter number)
                Graph object for ServoDesign plot
            :obj:`nqontrol.nqontrolUI.UIMonitor`
                realtime graph and target checklist etc
                :obj:`nqontrol.nqontrolUI.UIADwinMonitorChannels`


    Parameters
    ----------
    app : dash.Dash
        The dash app. For more information visit https://dash.plot.ly/.
    deviceNumber : :obj:`int`
        Specifies the :obj:`nqontrol.ServoDevice.deviceNumber`.

    Attributes
    ----------
    _numberOfServos : Integer
        Description of attribute `_numberOfServos`.
    _deviceNumber : :obj:`int`
        Specifies the :obj:`nqontrol.ServoDevice.deviceNumber`.
    __setUpComponents : type
        Description of attribute `__setUpComponents`.

    """

    def __init__(self, app, deviceNumber):
        super().__init__(app, deviceNumber)
        self._numberOfServos = settings.NUMBER_OF_SERVOS
        self.__setUpComponents()

    def __setUpComponents(self):
        # Initiates all subcomponents in a special method and puts them into their respective lists for better readability.
        self._uiServoSection = []
        self._uiRamps = []
        self._uiTempFeedbacks = []
        # self._uiAutoLocks = []
        for servoNumber in range(1, self._numberOfServos + 1):
            self._uiServoSection.append(UIServoSection(self._app, self._deviceNumber, servoNumber))
            self._uiRamps.append(UIRamp(self._app, self._deviceNumber, servoNumber))
            self._uiTempFeedbacks.append(UITempFeedback(self._app, self._deviceNumber, servoNumber))
            # self._uiAutoLocks.append(UIAutoLock(self._app, self._deviceNumber, servoNumber))
        self._uiSDPlot = UIServoDesignPlot(self._app, self._deviceNumber)
        self._monitor = UIMonitor(self._app, self._deviceNumber)

    @property
    def layout(self):
        """Return the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        header = [
            html.Div(
                children=[
                    # Device No. Picker
                    html.H1('ADwin Device No. {}'.format(self._deviceNumber), className='col-auto col-sm-7 col-lg-auto align-self-center'),
                    # Workload and timestamp
                    html.Div(
                        children=['Workload: {} Timestamp {}'.format(0, 0)],
                        id='work_time_{}'.format(self._deviceNumber),
                        className='col-auto ml-sm-auto ml-md-auto ml-lg-auto align-self-center'
                    )
                ],
                className='row justify-content-start align-items-center'
            ),
            html.Div(
                children=[
                    # Ramp target
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(children=['Ramp'], className='col-2 align-self-center'),
                                    dcc.RadioItems(
                                        options=[{'label': 'Off', 'value': 0}] + [{'label': i, 'value': i}
                                                                                  for i in range(1, self._numberOfServos + 1)],
                                        value=controller.getCurrentRampLocation(self._deviceNumber),
                                        id='rampTarget_{}'.format(self._deviceNumber),
                                        className='col-10',
                                        inputClassName='form-check-input',
                                        labelClassName='form-check form-check-inline'
                                    ),
                                    # html.Div(
                                    #     children=['AutoLock'],
                                    #     className='col-2 align-self-center'
                                    # ),
                                    # dcc.Checklist(
                                    #     options=[{'label': i, 'value': i} for i in range(1, self._numberOfServos + 1)],
                                    #     value=controller.getAutolockList(self._deviceNumber),
                                    #     id='autolockChecklist_{}'.format(self._deviceNumber),
                                    #     className='pl-0 col-10',
                                    #     inputClassName='form-check-input',
                                    #     labelClassName='form-check form-check-inline'
                                    # )
                                ],
                                className='row'
                            )
                        ],
                        className='col-12 col-md-6'
                    ),
                    # Save filename
                    html.Div(
                        children=[
                            dcc.Input(
                                placeholder='Save as...',
                                className='form-control',
                                value=controller.getCurrentSaveName(),
                                id='save_name_{}'.format(self._deviceNumber),
                            )
                        ],
                        className='col-6 col-md-2 col-lg-2 ml-lg-auto ml-xl-auto'
                    ),
                    # Save Button
                    html.Div(
                        children=[
                            html.Button(
                                'Save',
                                id='device_save_button_{}'.format(self._deviceNumber),
                                className='btn btn-primary w-100',
                            )
                        ],
                        className='col-3 col-md-2 col-lg-auto pl-0'
                    ),
                    # Reboot Button
                    html.Div(
                        children=[
                            html.Button(
                                'Reboot',
                                id='device_reboot_button_{}'.format(self._deviceNumber),
                                className='btn btn-primary w-100',
                            )
                        ],
                        className='col-3 col-md-2 col-lg-auto pl-0'
                    ),
                    # Error message output
                    dcc.Store(
                        id='error_{}'.format(self._deviceNumber),
                    ),
                    dcc.Store(id='save_out_{}'.format(self._deviceNumber))
                ],
                className='row justify-content-start align-items-center'
            )]
        servoDetails = [
            html.Details(
                children=[
                    html.Summary(
                        children=[
                            html.Span(
                                [controller.getServoName(self._deviceNumber, i)], id='servoName_{0}_{1}'.format(self._deviceNumber, i),
                                style={'width': '50%'}
                            ),
                            # html.Span(
                            #     [controller.getLockStatus(self._deviceNumber, i)],
                            #     id='servoStatus_{0}_{1}'.format(self._deviceNumber, i),
                            #     style={'width': '50%', 'text-align': 'right'}
                            # )
                        ],
                        className='col-12 d-flex',
                    ),
                    # within the details component there needs to be another div wrapper for some reason. if removed, the servo and ramp sections will align as if on separate rows. Since bootstrap also requires the nesting of col- classes within row-classes, the structure looks a bit unreadable
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    # Servo controls, including Input, Offset, Gain, Filters, Output
                                    self._uiServoSection[i - 1].layout,
                                    # Ramp sliders
                                    self._uiRamps[i - 1].layout
                                ],
                                className='row'
                            ),
                            # this is an ugly version to wrap it... buuut hey.
                            html.Div(
                                children=[
                                    html.Div(
                                        [self._uiTempFeedbacks[i - 1].layout],
                                        className='col-12 col-md-6 p-0 m-0'
                                    ),
                                    # html.Div(
                                    #     [self._uiAutoLocks[i - 1].layout],
                                    #     className='col-12 col-md-6 p-0 m-0'
                                    # )
                                ],
                                className='row'
                            ),
                            html.Div(
                                children=[
                                    html.P('Name', className='col-auto mb-0'),
                                    html.Div(
                                        children=[
                                            dcc.Input(
                                                id='servoNameInput_{0}_{1}'.format(self._deviceNumber, i),
                                                className='form-control'
                                            )
                                        ],
                                        className='col col-sm-4 col-md-2'
                                    ),
                                ],
                                className='row align-items-center justify-content-end'
                            )
                        ],
                        className='col-12'
                    )
                ],
                className='row p-0',  # each html.Detail is a bootstrap row
                style={'margin': '.1vh .5vh', 'border': '.5px solid #006dcc', 'border-radius': '4.5px'}
            ) for i in range(1, self._numberOfServos + 1)]  # List of html.Details, creating these one by one would be tedious
        rest = [
            html.Div(
                children=[
                    # ServoDesign Plot
                    self._uiSDPlot.layout,
                    # The Monitoring part of the Servo
                    self._monitor.layout
                ],
                className='row'
            ),
            # # Update timer
            # dcc.Interval(
            #     id='update_{}'.format(self._deviceNumber),
            #     interval=2000,
            #     n_intervals=0
            # )
        ]
        return header + servoDetails + rest  # In this case, no Dash html.Div is returned but the pure list of elements. All elements are rows and the main UI object has a Bootstrap ContainerFluid as its wrapping component

    def setCallbacks(self):
        """The function initiating all callbacks for the given element.
        """
        for i in range(1, self._numberOfServos + 1):
            # Pass along the servo number here since class has no specific servoNumber field
            # Technically these are callbacks of individual servo sections
            # Define the callback for the Servo Name input
            # servo name save file filename
            dynamically_generated_function = self.__createServoNameCallback(i)
            self._app.callback(
                Output('servoName_{0}_{1}'.format(self._deviceNumber, i), 'children'),
                [Input('servoNameInput_{0}_{1}'.format(self._deviceNumber, i), 'n_submit')],
                [State('servoNameInput_{0}_{1}'.format(self._deviceNumber, i), 'value')]
            )(dynamically_generated_function)

            # # Servo status callback
            # dynamically_generated_function = self.__createLockStatusCallback(i)
            # self._app.callback(
            #     Output('servoStatus_{0}_{1}'.format(self._deviceNumber, i), 'children'),
            #     [Input('update_{}'.format(self._deviceNumber), 'n_intervals'),
            #     Input('lockSlider_{0}_{1}'.format(self._deviceNumber, i), 'value'),
            #     Input()]
            # )(dynamically_generated_function)

        self.__setDeviceCallbacks()
        for componentList in (self._uiServoSection, self._uiRamps, self._uiTempFeedbacks):  # , self._uiAutoLocks is commented out
            for unit in componentList:
                unit.setCallbacks()

        self._monitor.setCallbacks()
        self._uiSDPlot.setCallbacks()

    # def __createLockStatusCallback(self, servoNumber):
    #     def callback(n_interval):
    #         return controller.getLockStatus(self._deviceNumber, servoNumber)
    #     return callback

    # Callbacks for the device control, e.g. timestamp and workload.
    def __setDeviceCallbacks(self):

        worktime = 'work_time_{}'.format(self._deviceNumber)
        dynamically_generated_function = self.__createWorkTimeCallback(worktime)
        self._app.callback(
            Output(worktime, 'children'),
            [Input('update_{}'.format(self._deviceNumber), 'n_intervals')]
        )(dynamically_generated_function)

        reboot = 'device_reboot_button_{}'.format(self._deviceNumber)
        dynamically_generated_function = self.__createRebootCallback(reboot)
        self._app.callback(
            Output('error_{}'.format(self._deviceNumber), 'data'),
            [Input(reboot, 'n_clicks')]
        )(dynamically_generated_function)

        ramp_servo_target = 'rampTarget_{}'.format(self._deviceNumber)
        dynamically_generated_function = self.__createRampCallback()
        self._app.callback(
            Output('rampInfo_{}'.format(self._deviceNumber), 'data'),
            [Input(ramp_servo_target, 'value')]
        )(dynamically_generated_function)

        # autolockChecklist = 'autolockChecklist_{}'.format(self._deviceNumber)
        # dynamically_generated_function = self.__createAutolockCallback()
        # self._app.callback(
        #     Output('rampTarget_{}'.format(self._deviceNumber), 'value'),  # enabling an autolock disables the ramp
        #     [Input(autolockChecklist, 'value'),
        #      # Input(ramp_servo_target, 'value')
        #      ]
        # )(dynamically_generated_function)

        saveTextArea = 'save_name_{}'.format(self._deviceNumber)
        saveButton = 'device_save_button_{}'.format(self._deviceNumber)
        dynamically_generated_function = self.__createSaveCallback()
        self._app.callback(
            Output('save_out_{}'.format(self._deviceNumber), 'data'),
            [Input(saveButton, 'n_clicks'),
             Input(saveTextArea, 'n_submit')],
            [State(saveTextArea, 'value')]
        )(dynamically_generated_function)

    # Callback for assigning a name to the individual servos
    def __createServoNameCallback(self, servoNumber):
        def callback(submit, name):
            return controller.callServoName(self._deviceNumber, servoNumber, submit, name)
        return callback

    # Callback for Save Button
    def __createSaveCallback(self):
        def callback(n_button, submit, filename):
            return controller.callSave(n_button, filename, self._deviceNumber)
        return callback

    # Callback for the RAMP switch
    def __createRampCallback(self):
        def callback(targetInput):
            return controller.callToggleRamp(targetInput, self._deviceNumber)
        return callback

    # AutoLock callback
    def __createAutolockCallback(self):
        def callback(value):
            return controller.callAutolock(value, self._deviceNumber)
        return callback

    # Reboot button
    def __createRebootCallback(self, inputElement):
        def callback(clicks):
            return controller.callReboot(clicks, self._deviceNumber)
        return callback

    # Workload output
    def __createWorkTimeCallback(self, output):
        def callback(input):
            return controller.callWorkloadTimestamp(self._deviceNumber)
        return callback


class UIServoSection(UIComponent):

    def __init__(self, app, deviceNumber, servoNumber):
        super().__init__(app, deviceNumber)
        self._servoNumber = servoNumber

    def setCallbacks(self):
        """The function initiating all callbacks for the given element.
        """

        # Offset callback
        offset = 'offset_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        sensitivityDropdown = 'input_sensitivity_dropdown_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        dynamically_generated_function = self.__createOffsetCallback()
        self._app.callback(
            Output('offset_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'children'),
            [Input(offset, 'n_submit'),
             Input(sensitivityDropdown, 'value')],
            [State(offset, 'value')]
        )(dynamically_generated_function)

        # Gain callback
        gain = 'gain_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        gainStore = 'gainStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        dynamically_generated_function = self.__createGainCallback()
        self._app.callback(
            Output('gain_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'children'),
            [Input(gain, 'n_submit'),
             Input('sosSwitchStorage_{}'.format(self._deviceNumber), 'data')],
            [State(gain, 'value')]
        )(dynamically_generated_function)

        # Gain Store Callback
        dynamically_generated_function = self.__storeLastGainTimestamp()
        self._app.callback(
            Output(gainStore, 'data'),
            [Input('gain_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'children')],
            [State(gain, 'n_submit_timestamp')]
        )(dynamically_generated_function)

        # Servo channels callback
        inputCheck = 'inputSectionCheck_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        filterCheck = 'filterSectionCheck_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        outputCheck = 'outputSectionCheck_{0}_{1}'.format(self._deviceNumber, self._servoNumber)

        dynamically_generated_function = self.__createChannelCallback()
        self._app.callback(
            Output('channelChecklistStorage_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'data'),
            [Input(inputCheck, 'value'), Input(outputCheck, 'value')]
        )(dynamically_generated_function)

        dynamically_generated_function = self.__createFilterCallback()
        self._app.callback(
            Output('filterChecklistStorage_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'data'),
            [Input(filterCheck, 'value')]
        )(dynamically_generated_function)

        # Input sensitivity callback initialization
        dynamically_generated_function = self.__createInputSensitivityCallback()
        # corresponding html ids
        label = 'input_sens_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        dropdown = 'input_sensitivity_dropdown_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # callback definition
        self._app.callback(
            Output(label, 'children'),
            [Input(dropdown, 'value')]
        )(dynamically_generated_function)

        # Aux sensitivity callback init
        dynamically_generated_function = self.__createAuxSensitivityCallback()
        # corresponding html ids
        label = 'aux_sens_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        dropdown = 'aux_sensitivity_dropdown_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # callback definition
        self._app.callback(
            Output(label, 'children'),
            [Input(dropdown, 'value')]
        )(dynamically_generated_function)

        # Snap parameters callback
        # snapGreater = 'snapGreater_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # snapLimit = 'snapLimit_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # snapLabel = 'snapLabel_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # dynamically_generated_function = self.__createSnapCallback()
        # self._app.callback(
        #     Output(snapLabel, 'children'),
        #     [Input(snapLimit, 'n_submit'),
        #      Input(snapGreater, 'value')],
        #     [State(snapLimit, 'value'),
        #      State(snapGreater, 'value')]
        # )(dynamically_generated_function)

    @property
    def layout(self):
        """Returns the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        return html.Div(
            children=[
                html.Div([
                    # Input Section
                    html.Div(
                        [
                            html.H3('Input', className='w-100 mt-0 pl-0'),
                            dcc.Checklist(
                                options=[
                                    {'label': 'Input', 'value': 'input'},
                                    {'label': 'Offset', 'value': 'offset'},
                                ],
                                value=controller.getInputStates(self._deviceNumber, self._servoNumber),
                                id='inputSectionCheck_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                className='w-100 pl-0',
                                inputClassName='form-check-input',
                                labelClassName='form-check'
                            ),
                            html.P('Input sensitivity (Limit: V, Mode: )', className='w-100 mb-0',
                                   id='input_sens_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber)),
                            html.Div(
                                [
                                    html.Div(
                                        [dcc.Dropdown(
                                            options=[{'label': i, 'value': i} for i in range(4)],
                                            value=controller.getInputSensitivity(self._deviceNumber, self._servoNumber),
                                            clearable=False,
                                            id='input_sensitivity_dropdown_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
                                        )],
                                        className='col-12 align-self-center'
                                    ),
                                ],
                                className='row'
                            ),
                        ],
                        className='col-3',
                    ),
                    # Offset and Gain, also part of the input
                    html.Div(
                        children=[
                            html.P('Offset', id='offset_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber)),
                            dcc.Input(
                                placeholder='-10 bis 10V',
                                value=controller.getOffset(self._deviceNumber, self._servoNumber),
                                id='offset_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                className='form-control'
                            ),
                            # Gain
                            html.P('Gain', id='gain_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber)),
                            dcc.Input(
                                placeholder='Enter gain...',
                                value=controller.getGain(self._deviceNumber, self._servoNumber),
                                id='gain_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                className='form-control'
                            ),
                            # # Snap
                            # html.P('Snap', id='snapLabel_{0}_{1}'.format(self._deviceNumber, self._servoNumber)),
                            # # The snapping condition dropdown
                            # dcc.Dropdown(
                            #     options=[
                            #         {'label': '>', 'value': True},
                            #         {'label': '<', 'value': False}
                            #     ],
                            #     value=controller.getSnapGreater(self._deviceNumber, self._servoNumber),
                            #     clearable=False,
                            #     id='snapGreater_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                            #     className='w-100 m-0'
                            # ),
                            # # the input field for the snap voltage limit
                            # dcc.Input(
                            #     placeholder='snap limit',
                            #     id='snapLimit_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                            #     value=controller.getSnapLimit(self._deviceNumber, self._servoNumber),
                            #     className='form-control w-100'
                            # ),
                            # Store component in order to determine how callGain was triggered. Saves previous timestamp
                            dcc.Store(
                                id='gainStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
                            ),
                            # Storage component to use as input channels checklist target in callbacks
                            dcc.Store(id='channelChecklistStorage_{0}_{1}'.format(self._deviceNumber, self._servoNumber)),
                        ],
                        className='col-3'
                    ),
                    # Filter section of the servo controls
                    html.Div(
                        children=[
                            html.H3('Filters', className='w-100 mt-0 pl-0'),
                            # Filter checklist
                            dcc.Checklist(
                                options=controller.getFilterLabels(self._deviceNumber, self._servoNumber),
                                value=controller.getActiveFilters(self._deviceNumber, self._servoNumber),
                                id='filterSectionCheck_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                className='w-100',
                                inputClassName='form-check-input',
                                labelClassName='form-check'
                            ),
                            # Storage component to use as target for filter checklist target in callback
                            dcc.Store(id='filterChecklistStorage_{0}_{1}'.format(self._deviceNumber, self._servoNumber)),
                        ],
                        className='col-3'
                    ),
                    # Output section of the servo controls
                    html.Div(
                        [
                            html.H3('Output', className='w-100 mt-0 pl-0'),
                            # Channel Checklist for 'Aux' and 'Output'
                            dcc.Checklist(
                                options=[
                                    {'label': 'Aux', 'value': 'aux'},
                                    # {'label': 'Snap', 'value': 'snap'},
                                    {'label': 'Output', 'value': 'output'},
                                ],
                                value=controller.getOutputStates(self._deviceNumber, self._servoNumber),
                                id='outputSectionCheck_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                className='w-100 pl-0',
                                inputClassName='form-check-input',
                                labelClassName='form-check'
                            ),
                            html.P('Aux sensitivity (Limit: V, Mode: )', className='w-100 mb-0',
                                   id='aux_sens_label_{0}_{1}'.format(self._deviceNumber, self._servoNumber)),
                            # The Aux sensitivity dropdown control
                            html.Div(
                                # For some input components it helps to wrap them in an extra div and set that Div's properties instead, since the Dropdown will align with it. Therefore the nested row/col wrapper
                                [
                                    html.Div(
                                        [dcc.Dropdown(
                                            options=[{'label': i, 'value': i} for i in range(4)],
                                            value=controller.getAuxSensitivity(self._deviceNumber, self._servoNumber),
                                            clearable=False,
                                            id='aux_sensitivity_dropdown_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
                                        )],
                                        className='col-12 align-self-center'
                                    ),
                                ],
                                className='row'
                            ),
                        ],
                        className='col-3',
                    )],
                    className='row'
                )
            ],
            className='col-12 col-xl-6 d-inline'
        )

    # Callback for the snap section
    # def __createSnapCallback(self):
    #     def callback(submit, dropdown, limit, greater):
    #         return controller.callSnapParam(limit, greater, self._servoNumber, self._deviceNumber)
    #     return callback

    # Callback for the Offset Input Field
    def __createOffsetCallback(self):
        def callback(n_submit, dropdownTrigger, inputValue):
            return controller.callOffset(self._deviceNumber, self._servoNumber, inputValue)
        return callback

    # Callback for the Gain Input Field
    def __createGainCallback(self):
        def callback(n_submit, sosTrigger, inputValue):
            context = dash.callback_context
            return controller.callGain(context, self._deviceNumber, self._servoNumber, inputValue)
        return callback

    def __storeLastGainTimestamp(self):
        def callback(input, timestamp):
            return timestamp
        return callback

    # Callback for the input channels checklist
    def __createChannelCallback(self):
        def callback(inputValues, inputValues2):
            return controller.callServoChannels(self._deviceNumber, self._servoNumber, inputValues + inputValues2)
        return callback

    def __createFilterCallback(self):
        def callback(value):
            return controller.callToggleServoFilters(self._deviceNumber, self._servoNumber, value)
        return callback

    def __createAuxSensitivityCallback(self):
        def callback(selected):
            return controller.callAuxSensitivity(selected, self._deviceNumber, self._servoNumber)
        return callback

    def __createInputSensitivityCallback(self):
        def callback(selected):
            return controller.callInputSensitivity(selected, self._deviceNumber, self._servoNumber)
        return callback


class UIRamp(UIComponent):
    def __init__(self, app, deviceNumber, servoNumber):
        super().__init__(app, deviceNumber)
        self._servoNumber = servoNumber

    @property
    def layout(self):
        """Return the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        return html.Div(
            children=[
                # Ramp title and current ramp
                html.Div(
                    children=[
                        html.H3('Ramp', className='col-auto mt-0'),
                        html.Span(id='current_ramp_{0}_{1}'.format(self._deviceNumber, self._servoNumber), className='col-auto')
                    ],
                    className='row justify-content-between align-items-center'
                ),
                # Amplitude label and slider
                html.Div(
                    children=[
                        html.P(
                            'Amplitude',
                            className='col-12'
                        ),
                        dcc.Slider(
                            id='ramp_amp_slider_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                            min=0.1,
                            max=10,
                            step=.05,
                            value=controller.getServoAmplitude(self._deviceNumber, self._servoNumber),
                            marks={i: '{}'.format(i) for i in range(1, 11, 1)},
                            className='col-10',
                            updatemode='drag'
                        )
                    ],
                    className='row justify-content-center'
                ),
                # Frequency label and slider
                html.Div(
                    children=[
                        html.P(
                            'Frequency',
                            className='col-12'
                        ),
                        dcc.Slider(
                            id='ramp_freq_slider_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                            min=controller.getServoMinFrequency(self._deviceNumber, self._servoNumber),
                            max=controller.getServoMaxFrequency(self._deviceNumber, self._servoNumber),
                            step=controller.getServoFrequencyStep(self._deviceNumber, self._servoNumber),
                            value=controller.getServoFrequency(self._deviceNumber, self._servoNumber),
                            marks={i: '{}'.format(i) for i in range(int(controller.getServoMinFrequency(
                                self._deviceNumber, self._servoNumber)) - 1, int(controller.getServoMaxFrequency(self._deviceNumber, self._servoNumber)) + 1, 50)},
                            className='col-10',
                            updatemode='drag'
                        ),
                    ],
                    className='row justify-content-center',
                )
            ],
            className='col-12 col-xl-6 d-inline'
        )

    # Callback for the Ramp unit's amplitude slider
    def __createRampCallback(self):
        def callback(amp, freq):
            context = dash.callback_context
            return controller.callRamp(amp, freq, context, self._deviceNumber, self._servoNumber)
        return callback

    def setCallbacks(self):
        ramp_freq_slider = 'ramp_freq_slider_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        ramp_amp_slider = 'ramp_amp_slider_{0}_{1}'.format(self._deviceNumber, self._servoNumber)

        amp_out = 'current_ramp_{0}_{1}'.format(self._deviceNumber, self._servoNumber)

        dynamically_generated_function = self.__createRampCallback()
        self._app.callback(
            Output(amp_out, 'children'),
            [Input(ramp_amp_slider, 'value'),
             Input(ramp_freq_slider, 'value')],
        )(dynamically_generated_function)


class UIServoDesignPlot(UIComponent):
    def __init__(self, app, deviceNumber):
        super().__init__(app, deviceNumber)
        self._uiSOSSection = UISecondOrderSection(self._app, self._deviceNumber)

    @property
    def layout(self):
        return html.Div(
            children=[
                html.H2('Servo Design'),
                html.Div([self._uiSOSSection.layout], className='row'),
                html.Div(
                    children=[
                        html.Div(['Plots the Second Order Section implemented by the Servo Design.'], className='col-12'),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id='sdGraph_{}'.format(self._deviceNumber),
                                    animate=False,
                                )
                            ],
                            className='col-12'
                        )
                    ],
                    className='row'
                ),
            ],
            className='col-12 col-lg-6',
        )

    def _createGraphCallback(self):
        def callback(unplantTrigger, *args):
            return controller.callPlotServoDesign(self._deviceNumber)
        return callback

    def setCallbacks(self):
        self._uiSOSSection.setCallbacks()

        graph = 'sdGraph_{}'.format(self._deviceNumber)
        uploadOutput = 'uploadOutput{}'.format(self._deviceNumber)
        inputs = [Input(uploadOutput, 'data')]

        for i in range(5):
            inputs.append(Input('filter_update_{0}_{1}'.format(self._deviceNumber, i), 'data'))

        inputs.append(Input('sos_gain_label_{}'.format(self._deviceNumber), 'children'))

        dynamically_generated_function = self._createGraphCallback()
        self._app.callback(
            Output(graph, 'figure'),
            inputs
        )(dynamically_generated_function)


class UISecondOrderSection(UIComponent):

    def __init__(self, app, deviceNumber):
        super().__init__(app, deviceNumber)
        self._uiFilters = [UIFilter(self._app, self._deviceNumber, filterIndex)
                           for filterIndex in range(controller.getMaxFilters(deviceNumber))]

    @property
    def layout(self):
        """Return the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        # Needing a content list beforehand
        childrenList = [
            html.Div(
                children=[
                    # Servo number target
                    html.Div(
                        children=[
                            dcc.Input(
                                type='number',
                                min=1,
                                max=settings.NUMBER_OF_SERVOS,
                                value=1,
                                id='sos_servo_{}'.format(self._deviceNumber),
                                className='form-control'
                            )
                        ],
                        className='col-3 col-sm-2 pr-0'
                    ),
                    # Upload field
                    html.Div(
                        [dcc.Upload(
                            children=html.Div('Upload plant.'),
                            id='plantUpload{}'.format(self._deviceNumber),
                            style={
                                'height': '2.25rem',
                                'line-height': '2.25rem',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0'
                            },
                            className='wl-100'
                        )],
                        className='col-9 col-sm-4'
                    ),
                    # Unplant button
                    html.Div(
                        [html.Button(
                            'Unplant',
                            id='sosDelPlant_{0}'.format(self._deviceNumber),
                            className='btn btn-primary w-100',
                        )],
                        className='col-6 ml-sm-auto col-sm-2 col-lg-auto pl-sm-0'
                    ),
                    # Apply button
                    html.Div(
                        [html.Button(
                            'Apply',
                            id='sos_apply_{0}'.format(self._deviceNumber),
                            className='btn btn-primary w-100'
                        )],
                        className='col-6 col-sm-2 col-lg-auto pl-sm-0'
                    ),
                    dcc.Store(id='sosSwitchStorage_{}'.format(self._deviceNumber)),

                ],
                className='row align-items-center'
            ),
            html.Div(
                children=[
                    # Gain label
                    html.Div(
                        ['Gain'],
                        id='sos_gain_label_{}'.format(self._deviceNumber),
                        className='col-3 col-sm-2'
                    ),
                    # Gain input field
                    html.Div(
                        [
                            dcc.Input(
                                placeholder='Enter gain...',
                                value=controller.getSDGain(self._deviceNumber),
                                id='sos_gain_{}'.format(self._deviceNumber),
                                className='form-control w-100'
                            )
                        ],
                        className=' col-3 col-sm-4 pl-0 pl-sm-3'
                    ),
                    # Plant button timestamp storage to determine how controller.callPlantParse was triggered
                    dcc.Store(
                        id='uploadOutput{}'.format(self._deviceNumber),
                    )
                ],
                className='row align-items-center'
            )
        ]
        for uiFilter in self._uiFilters:
            childrenList.append(uiFilter.layout)
        return html.Div(
            id='sos_unit_{0}'.format(self._deviceNumber),
            children=childrenList,
            className='col-12',
        )

    def _createUploadCallback(self):
        def callback(filename, contents, n_clicks, timestamp, timestamp_old):
            return controller.callPlantParse(self._deviceNumber, filename, contents, n_clicks, timestamp, timestamp_old)
        return callback

    def _createApplyServoCallback(self):
        def callback(n_clicks, servoNumber):
            return controller.callApplyServoDesign(servoNumber, self._deviceNumber, n_clicks)
        return callback

    def _applyLabelCallback(self, servoNumber):
        def callback(value, applyNumber, n_clicks):
            return controller.callApplyFilterLabels(applyNumber, servoNumber, self._deviceNumber, n_clicks)
        return callback

    def _applyValuesCallback(self, servoNumber):
        def callback(hiddenInput, applyNumber, n_clicks):
            return controller.callApplyFilterValues(applyNumber, servoNumber, self._deviceNumber, n_clicks)
        return callback

    # Callback for the SOS Gain Input Field
    def __createSOSGainCallback(self):
        def callback(inputValue):
            return controller.callServoDesignGain(inputValue, self._deviceNumber)
        return callback

    def setCallbacks(self):
        """Initialize all callbacks for the given element."""
        for filter in self._uiFilters:
            filter.setCallbacks()

        for i in range(1, settings.NUMBER_OF_SERVOS + 1):
            sectionCheck = 'filterSectionCheck_{0}_{1}'.format(self._deviceNumber, i)

            # Apply the values
            dynamically_generated_function = self._applyValuesCallback(i)
            self._app.callback(
                Output(sectionCheck, 'value'),
                [Input('sosSwitchStorage_{}'.format(self._deviceNumber), 'data')],
                [State('sos_servo_{}'.format(self._deviceNumber), 'value'),
                 State('sos_apply_{}'.format(self._deviceNumber), 'n_clicks')]
            )(dynamically_generated_function)

            # Apply the labels
            dynamically_generated_function = self._applyLabelCallback(i)
            self._app.callback(
                Output(sectionCheck, 'options'),
                [Input(sectionCheck, 'value')],
                [State('sos_servo_{}'.format(self._deviceNumber), 'value'),
                 State('sos_apply_{}'.format(self._deviceNumber), 'n_clicks')]
            )(dynamically_generated_function)

        delPlant = 'sosDelPlant_{0}'.format(self._deviceNumber)
        plantUpload = 'plantUpload{}'.format(self._deviceNumber)

        dynamically_generated_function = self._createUploadCallback()
        self._app.callback(
            Output('uploadOutput{}'.format(self._deviceNumber), 'data'),
            [Input(plantUpload, 'filename'),
             Input(plantUpload, 'contents'),
             Input(delPlant, 'n_clicks')],
            [State(delPlant, 'n_clicks_timestamp'),
             State('uploadOutput{}'.format(self._deviceNumber), 'data')]
        )(dynamically_generated_function)

        dynamically_generated_function = self._createApplyServoCallback()
        self._app.callback(
            Output('sosSwitchStorage_{}'.format(self._deviceNumber), 'data'),
            [Input('sos_apply_{}'.format(self._deviceNumber), 'n_clicks')],
            [State('sos_servo_{}'.format(self._deviceNumber), 'value')]
        )(dynamically_generated_function)

        # Gain callback
        gain = 'sos_gain_{}'.format(self._deviceNumber)
        dynamically_generated_function = self.__createSOSGainCallback()
        self._app.callback(
            Output('sos_gain_label_{}'.format(self._deviceNumber), 'children'),
            [Input(gain, 'value')]
        )(dynamically_generated_function)


class UIFilter(UIComponent):

    def __init__(self, app, deviceNumber, filterIndex):
        super().__init__(app, deviceNumber)
        self._filterIndex = filterIndex

    @property
    def layout(self):
        """Returns the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        # Setting up dropdown options
        options = [{'label': 'None', 'value': None}]
        for filter in controller.getFilterOptions():
            options.append({'label': filter.__name__, 'value': filter.__name__})
        return html.Div(
            children=[
                # Active checkbox
                html.Div(
                    [dcc.Checklist(
                        id='filter_active_{0}_{1}'.format(self._deviceNumber, self._filterIndex),
                        options=[
                            {'label': '', 'value': self._filterIndex},
                        ],
                        value=controller.getFilterEnabled(self._deviceNumber, self._filterIndex),
                        inputClassName='form-check-input',
                        labelClassName='form-check form-check-inline',
                    )],
                    className='col-2 col-sm-auto'
                ),
                # Dropdown filter type selection
                html.Div(
                    children=[
                        dcc.Dropdown(
                            options=options,
                            id='filter_unit_dropdown_{0}_{1}'.format(self._deviceNumber, self._filterIndex),
                            value=controller.getFilterDropdown(self._deviceNumber, self._filterIndex)
                        )
                    ],
                    className='col-10 col-sm-3 col-lg-3'
                ),
                # Main filter parameter
                html.Div(
                    children=[
                        dcc.Input(
                            id='filter_frequency_input_{0}_{1}'.format(self._deviceNumber, self._filterIndex),
                            placeholder='fc',
                            className='form-control',
                            value=controller.getFilterMainPar(self._deviceNumber, self._filterIndex)
                        )
                    ],
                    className='col-5 col-sm pl-sm-0 pr-0 pr-sm-3 ml-auto ml-sm-0'
                ),
                # Secondary filter parameter (optional)
                html.Div(
                    children=[
                        dcc.Input(
                            id='filter_optional_input_{0}_{1}'.format(self._deviceNumber, self._filterIndex),
                            placeholder='fcslope',
                            className='form-control',
                            value=controller.getFilterSecondPar(self._deviceNumber, self._filterIndex)
                        )
                    ],
                    className='col-5 col-sm pl-0'
                ),
                # Description
                html.Div(
                    [controller.getFilterDescription(self._deviceNumber, self._filterIndex)], id='filter_description_{0}_{1}'.format(self._deviceNumber, self._filterIndex),
                    className='col-10 col-sm-5 col-lg-4 filter-font ml-auto ml-sm-0 pl-sm-0'
                ),
                dcc.Store(id='filter_update_{0}_{1}'.format(self._deviceNumber, self._filterIndex))
            ],
            className='row justify-content-start align-items-center'
        )

    # Callback for visibility of filter input fields
    def _createFilterFieldCallback(self):
        def callback(dropdownInput, mainInput, secInput, servoTarget, plant, active, dropdown, main, sec, activeState):
            return controller.callFilterField(dropdown, main, sec, activeState, self._deviceNumber, self._filterIndex)
        return callback

    def _createDescriptionCallback(self):
        def callback(dropdown, main, sec):
            return controller.callFilterDescription(dropdown, main, sec, self._deviceNumber, self._filterIndex)
        return callback

    def _createVisibilityCallback(self):
        def callback(dropdownInput):
            return controller.callFilterVisible(dropdownInput)
        return callback

    def setCallbacks(self):
        """The function initiating all callbacks for the given element.
        """

        dropdown = 'filter_unit_dropdown_{0}_{1}'.format(self._deviceNumber, self._filterIndex)
        mainInput = 'filter_frequency_input_{0}_{1}'.format(self._deviceNumber, self._filterIndex)
        secInput = 'filter_optional_input_{0}_{1}'.format(self._deviceNumber, self._filterIndex)
        description = 'filter_description_{0}_{1}'.format(self._deviceNumber, self._filterIndex)
        updateDiv = 'filter_update_{0}_{1}'.format(self._deviceNumber, self._filterIndex)
        servoTarget = 'sos_servo_{}'.format(self._deviceNumber)
        activeCheck = 'filter_active_{0}_{1}'.format(self._deviceNumber, self._filterIndex)

        # Parameter/filter callback
        dynamically_generated_function = self._createFilterFieldCallback()
        self._app.callback(
            Output(updateDiv, 'data'),
            [Input(dropdown, 'value'), Input(mainInput, 'value'), Input(secInput, 'value'), Input(servoTarget, 'value'),
             Input('plantUpload{}'.format(self._deviceNumber), 'filename'), Input(activeCheck, 'value')],
            [State(dropdown, 'value'), State(mainInput, 'value'), State(secInput, 'value'), State(activeCheck, 'value')]
        )(dynamically_generated_function)

        # Visibility callbacks
        for elem in [mainInput, secInput, description]:
            dynamically_generated_function = self._createVisibilityCallback()
            self._app.callback(
                Output(elem, 'style'),
                [Input(dropdown, 'value')]
            )(dynamically_generated_function)

        # Description callback
        dynamically_generated_function = self._createDescriptionCallback()
        self._app.callback(
            Output(description, 'children'),
            [Input(dropdown, 'value'), Input(mainInput, 'value'), Input(secInput, 'value')]
        )(dynamically_generated_function)


class UIMonitor(UIComponent):

    def __init__(self, app, deviceNumber):
        super().__init__(app, deviceNumber)
        self._sendChannels = UIADwinMonitorChannels(app, deviceNumber)  # Init UI for physical monitor channels of ADwin device

    @property
    def layout(self):
        """Returns the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        self._layout = html.Div(
            # Monitoring Graph placeholder
            children=[
                # Monitor headline
                html.H2('Monitor'),
                # Servo target RadioItems
                html.Div(
                    children=[
                        html.Div('Servo', className='col-2 align-self-center'),
                        dcc.RadioItems(
                            options=[{'label': i, 'value': i}
                                     for i in range(1, settings.NUMBER_OF_SERVOS + 1)],
                            value=1,
                            id='monitorTarget_{}'.format(self._deviceNumber),
                            className='col-10',
                            inputClassName='form-check-input',
                            labelClassName='form-check form-check-inline'
                        ),
                        dcc.Store(
                            id='rampInfo_{}'.format(self._deviceNumber),
                        )
                    ],
                    className='row justify-content-start align-items-center'
                ),
                # Realtime graph
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id='monitor_graph_{}'.format(self._deviceNumber),
                                    animate=False,
                                )
                            ],
                            className='col-12 align-self-end'
                        )
                    ],
                    className='row'
                ),
                # Visible channels checklist
                html.Div(
                    children=[
                        html.Div(['Channels: '], className='col-auto d-inline'),
                        dcc.Checklist(
                            options=[
                                {'label': 'Input', 'value': 'input'},
                                {'label': 'Aux', 'value': 'aux'},
                                {'label': 'Output', 'value': 'output'}
                            ],
                            value=['input'],
                            inputClassName='form-check-input',
                            labelClassName='form-check form-check-inline',
                            id='monitor_check_{}'.format(self._deviceNumber),
                        ),
                        # Callback output
                        dcc.Store(id='checklistTarget_{}'.format(self._deviceNumber))
                    ],
                    className='row justify-content-start align-items-center'
                ),
                # Update timer
                dcc.Interval(
                    id='update_{}'.format(self._deviceNumber),
                    interval=1000,
                    n_intervals=0
                ),
                # Physical ADwin monitor channels
                self._sendChannels.layout,
            ],
            className='col-12 col-lg-6'
        )
        return self._layout

    def setCallbacks(self):
        """The function initiating all callbacks for the given element.
        """

        # callbacks of the component which sets the ADwins internal monitoring Channels
        self._sendChannels.setCallbacks()

        # relevant HTML Ids
        servoInput = 'monitorTarget_{}'.format(self._deviceNumber)
        graph = 'monitor_graph_{}'.format(self._deviceNumber)
        checkList = 'monitor_check_{}'.format(self._deviceNumber)
        update = 'update_{}'.format(self._deviceNumber)

        self._app.callback(
            Output(graph, 'figure'),
            [Input(update, 'n_intervals'), Input(servoInput, 'value')],
            [State(servoInput, 'value'), State(checkList, 'value')],
        )(self.__createMonitorCallback())

        self._app.callback(
            Output('checklistTarget_{}'.format(self._deviceNumber), 'data'),
            [Input(checkList, 'value')],
            [State(servoInput, 'value')]
        )(self.__createChannelCheckCallback())

    # Callback to the monitor
    def __createMonitorCallback(self):
        def callback(intervals, inputNum, servoNumber, checklistState):
            return controller.callMonitorUpdate(1, servoNumber, checklistState)
        return callback

    # Callback for checklist of visible monitor channels
    def __createChannelCheckCallback(self):
        def callback(visibleChannels, servoNumber):
            return controller.callMonitorUpdateChannels(1, servoNumber, visibleChannels)
        return callback


class UIADwinMonitorChannels(UIComponent):

    def __init__(self, app, deviceNumber):
        super().__init__(app, deviceNumber)

    @property
    def layout(self):
        """Returns the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        self._layout = html.Details(
            children=[
                html.Summary(
                    ['ADwin Monitor Channels'],
                    className='col-12'
                ),
                html.P("Send a servo channel to one of the ADwin's physical monitor outputs.", className='col'),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                # Channel index label
                                html.P('{}'.format(i), className='col-auto align-self-center m-0'),
                                # Servo target dropdown
                                html.Div(
                                    children=[
                                        dcc.Dropdown(
                                            options=[{'label': 'Servo {}'.format(j), 'value': j} for j in range(
                                                1, settings.NUMBER_OF_SERVOS + 1)],
                                            value=controller.getMonitorsServo(self._deviceNumber, i),
                                            placeholder='Servo channel',
                                            id='adwin_monitor_channel_target_{0}_{1}'.format(self._deviceNumber, i)
                                        )
                                    ],
                                    className='col'
                                ),
                                # Channel card dropdown
                                html.Div(
                                    children=[
                                        dcc.Dropdown(
                                            options=[
                                                {'label': 'Input', 'value': 'input'},
                                                {'label': 'Aux', 'value': 'aux'},
                                                {'label': 'Output', 'value': 'output'},
                                                {'label': 'TTL', 'value': 'ttl'},
                                            ],
                                            value=controller.getMonitorsCard(self._deviceNumber, i),
                                            placeholder='Card',
                                            id='adwin_monitor_channel_card_{0}_{1}'.format(self._deviceNumber, i)
                                        )
                                    ],
                                    className='col'
                                ),
                                dcc.Store(id='store_adwin_monitor_channel_{0}_{1}'.format(self._deviceNumber, i))],
                            className='row'
                        ) for i in range(1, settings.NUMBER_OF_MONITORS + 1)
                    ],
                    className='col-12',
                )
            ],
            className='row p-0',  # The detail itself is a row
            style={'margin': '.1vh .5vh', 'border': '.5px solid #006dcc', 'border-radius': '4.5px'}
        )
        return self._layout

    # The channel parameter is the monitor channel corresponding with the hardware channel on the device
    def __setADwinMonitorCallback(self, channel):
        # inp1 and inp2 are only used as triggers, servo and card refer to the servo that's being assigned to the channel and the monitoring data (input, output, aux, ttl)
        def callback(inp1, inp2, servo, card):
            return controller.callADwinMonitor(channel, servo, card, self._deviceNumber)
        return callback

    def setCallbacks(self):
        """The function initiating all callbacks for the given element.
        """

        for i in range(1, settings.NUMBER_OF_MONITORS + 1):
            # setting the function for each individual i
            dynamically_generated_function = self.__setADwinMonitorCallback(i)
            # all HTML IDs relevant to the callback
            servoDropdown = 'adwin_monitor_channel_target_{0}_{1}'.format(self._deviceNumber, i)
            cardDropdown = 'adwin_monitor_channel_card_{0}_{1}'.format(self._deviceNumber, i)
            # stores the information, mainly Output dummy
            store = 'store_adwin_monitor_channel_{0}_{1}'.format(self._deviceNumber, i)
            # configuring the callback
            self._app.callback(
                Output(store, 'data'),
                [Input(servoDropdown, 'value'),
                 Input(cardDropdown, 'value')],
                [State(servoDropdown, 'value'),
                 State(cardDropdown, 'value')]
            )(dynamically_generated_function)


class UITempFeedback(UIComponent):

    def __init__(self, app, deviceNumber, servoNumber):
        super().__init__(app, deviceNumber)
        self._servoNumber = servoNumber

    @property
    def layout(self):
        """Returns the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        self._layout = html.Details(
            children=[
                html.Summary(
                    ['Temperature Feedback Control'],
                    className='col-6'
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(['dT'], className='col-12 col-sm-4'),
                                html.Div(
                                    children=[
                                        dcc.Input(
                                            placeholder='dT',
                                            className='w-100 form-control',
                                            id='tempDt_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                        ),
                                        dcc.Store(id='dtStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber))
                                    ],
                                    className='col-12 col-sm-4'
                                ),
                            ],
                            className='row align-items-center'
                        ),
                        html.Div(
                            children=[
                                html.Div(['mtd'], className='col-12 col-sm-4'),
                                html.Div(
                                    children=[
                                        dcc.Input(
                                            placeholder='mtd port',
                                            className='w-100 form-control',
                                            id='tempMtdPort_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
                                        ),
                                    ],
                                    className='col-6 col-sm-4'
                                ),
                                html.Div(
                                    children=[
                                        dcc.Input(
                                            placeholder='mtd Num',
                                            className='w-100 form-control',
                                            id='tempMtdNum_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
                                        ),
                                    ],
                                    className='col-6 col-sm-4'
                                ),
                                dcc.Store(id='mtdStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber))
                            ],
                            className='row align-items-center'
                        ),
                        html.Div(
                            children=[
                                html.Div(['Interval'], className='col-12 col-sm-4'),
                                html.Div(
                                    children=[
                                        dcc.Input(
                                            placeholder='time [s]',
                                            className='w-100 form-control',
                                            id='tempInterval_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
                                        ),
                                        dcc.Store(id='intervalStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber))
                                    ],
                                    className='col-12 col-sm-4'
                                ),
                            ],
                            className='row align-items-center'
                        ),
                        html.Div(
                            children=[
                                html.Div(['Voltage limit'], className='col-12 col-sm-4'),
                                html.Div(
                                    children=[
                                        dcc.Input(
                                            placeholder='default 5',
                                            className='w-100 form-control',
                                            id='voltLim_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
                                        ),
                                        dcc.Store(id='voltStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber))
                                    ],
                                    className='col-12 col-sm-4'
                                ),
                                html.Div(
                                    children=[
                                        html.Button(
                                            'Start',
                                            id='tempToggle_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                            className='btn btn-primary w-100'
                                        )
                                    ],
                                    className='col-12 col-sm-4'
                                ),
                            ],
                            className='row align-items-center'
                        ),
                    ],
                    className='col-12'
                )
            ],
            className='row p-0 justify-items-start align-items-center',  # The detail itself is a row
            style={'margin': '.1vh .5vh'}
        )
        return self._layout

    def setCallbacks(self):
        """The function initiating all callbacks for the given element.
        """
        dt = 'tempDt_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        mtdport = 'tempMtdPort_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        mtdnum = 'tempMtdNum_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        interval = 'tempInterval_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        button = 'tempToggle_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        voltLim = 'voltLim_{0}_{1}'.format(self._deviceNumber, self._servoNumber)

        # Button callback
        dynamically_generated_function = self.__createButtonCallback()
        self._app.callback(
            Output(button, 'children'),
            [Input(button, 'n_clicks')],
            [State(dt, 'value'),
             State(mtdnum, 'value'),
             State(mtdport, 'value'),
             State(interval, 'value'),
             State(voltLim, 'value')],
        )(dynamically_generated_function)

        dtStore = 'dtStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # dT callback
        dynamically_generated_function = self.__createDtCallback()
        self._app.callback(
            Output(dtStore, 'data'),
            [Input(dt, 'n_submit')],
            [State(dt, 'value')]
        )(dynamically_generated_function)

        mtdStore = 'mtdStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # mtd callback
        dynamically_generated_function = self.__createMtdCallback()
        self._app.callback(
            Output(mtdStore, 'data'),
            [Input(mtdnum, 'n_submit'),
             Input(mtdport, 'n_submit')],
            [State(mtdnum, 'value'),
             State(mtdport, 'value')],
        )(dynamically_generated_function)

        intervalStore = 'intervalStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # Interval callbacks
        dynamically_generated_function = self.__createIntervalCallback()
        self._app.callback(
            Output(intervalStore, 'data'),
            [Input(interval, 'n_submit')],
            [State(interval, 'value')]
        )(dynamically_generated_function)

        voltStore = 'voltStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # Voltage limit callback
        dynamically_generated_function = self.__createVoltLimitCallback()
        self._app.callback(
            Output(voltStore, 'data'),
            [Input(voltLim, 'n_submit')],
            [State(voltLim, 'value')]
        )(dynamically_generated_function)

    def __createVoltLimitCallback(self):
        def callback(submit, value):
            return controller.callTempVoltageLimit(submit, value, self._servoNumber, self._deviceNumber)
        return callback

    def __createIntervalCallback(self):
        def callback(submit, value):
            return controller.callTempInterval(submit, value, self._servoNumber, self._deviceNumber)
        return callback

    def __createMtdCallback(self):
        def callback(numSubmit, portSubmit, num, port):
            return controller.callTempMtd(numSubmit, portSubmit, num, port, self._servoNumber, self._deviceNumber)
        return callback

    def __createDtCallback(self):
        def callback(submit, value):
            return controller.callTempDt(submit, value, self._servoNumber, self._deviceNumber)
        return callback

    def __createButtonCallback(self):
        def callback(clicks, dt, num, port, interval, voltLim):
            return controller.callTempButton(clicks, dt, num, port, interval, voltLim, self._servoNumber, self._deviceNumber)
        return callback


class UIAutoLock(UIComponent):

    def __init__(self, app, deviceNumber, servoNumber):
        super().__init__(app, deviceNumber)
        self._servoNumber = servoNumber

    @property
    def layout(self):
        """Returns the elements' structure to be passed to a Dash style layout, usually with html.Div() as a top level container. For additional information read the Dash documentation at https://dash.plot.ly/.

        Returns
        -------
        html.Div
            The html/dash layout.

        """
        self._layout = html.Details(
            children=[
                html.Summary(
                    ['AutoLock Parameters'],
                    className='col-6'
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(['Activate'], className='col-12 col-sm-4'),
                                html.Div(
                                    children=[
                                        ToggleSwitch(
                                            value=controller.getAutolockList(self._deviceNumber),
                                            id='autolock_{}_{}'.format(self._deviceNumber, self._servoNumber),
                                        ),
                                    ],
                                    className='col-12 col-sm-4'
                                ),
                            ],
                            className='row align-items-center'
                        ),
                        html.Div(
                            children=[
                                html.Div(['Threshold'], className='col-12 col-sm-4'),
                                html.Div(
                                    children=[
                                        dcc.Input(
                                            placeholder='Voltage',
                                            className='w-100 form-control',
                                            value=controller.getLockThreshold(self._deviceNumber, self._servoNumber),
                                            id='threshold_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                        ),
                                    ],
                                    className='col-12 col-sm-4'
                                ),
                            ],
                            className='row align-items-center'
                        ),
                        html.Div(
                            children=[
                                html.Div(['Greater?'], className='col-12 col-sm-4'),
                                html.Div(
                                    children=[
                                        dcc.Dropdown(
                                            options=[
                                                {'label': '>', 'value': True},
                                                {'label': '<', 'value': False}
                                            ],
                                            value=controller.getLockGreater(self._deviceNumber, self._servoNumber),
                                            clearable=False,
                                            id='lockGreater_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                            className='w-100 m-0'
                                        ),
                                    ],
                                    className='col-12 col-sm-4'
                                )
                            ],
                            className='row align-items-center'
                        ),
                        # html.Div(
                        #     children=[
                        #         html.Div(
                        #             children=[
                        #                 dcc.Checklist(
                        #                     options=[
                        #                         {'label': 'Auto-Relock', 'value': 'on'},
                        #                     ],
                        #                     value=controller.getLockRelock(self._deviceNumber, self._servoNumber),
                        #                     id='autoRelock_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                        #                     className='w-100 m-0',
                        #                     inputClassName='form-check-input',
                        #                     labelClassName='form-check form-check-inline'
                        #                 ),
                        #             ],
                        #             className='col-12 col-sm-4'
                        #         )
                        #     ],
                        #     className='row align-items-center'
                        # ),
                        html.Div(
                            children=[
                                html.Div(['Search Range'], className='col-12'),
                                dcc.RangeSlider(
                                    count=1,
                                    min=-10,
                                    max=10,
                                    step=.5,
                                    value=controller.getLockRange(self._deviceNumber, self._servoNumber),
                                    allowCross=False,
                                    id='lockSlider_{0}_{1}'.format(self._deviceNumber, self._servoNumber),
                                    className='col-10 mt-1',
                                    pushable=1,
                                    updatemode='drag',
                                    marks={i: '{}'.format(i) for i in range(-10, 11)},
                                ),
                            ],
                            className='row justify-content-center align-items-center'
                        ),
                    ],
                    className='col-12'
                )
            ],
            className='row p-0 justify-items-start align-items-center',  # The detail itself is a row
            style={'margin': '.1vh .5vh'}
        )
        return self._layout

    def setCallbacks(self):
        """The function initiating all callbacks for the given element.
        """
        # relock = 'autoRelock_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        # relockStore = 'autoRelockStore_{0}_{1}'.format(self._deviceNumber, self._servoNumber)
        #
        # dynamically_generated_function = self.__createRelockCallback()
        # self._app.callback(
        #     Output(relockStore, 'data'),
        #     [Input(relock, 'value')]
        # )(dynamically_generated_function)

        # Servo status callback
        # dynamically_generated_function = self.__createLockStatusCallback(self._servoNumber)
        # self._app.callback(
        #     Output('servoStatus_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'children'),
        #     [Input('update_{}'.format(self._deviceNumber), 'n_intervals'),
        #      Input('autolock_{}_{}'.format(self._deviceNumber, self._servoNumber), 'value'),
        #      Input('lockSlider_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'value'),
        #      Input('threshold_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'n_submit'),
        #      Input('lockGreater_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'value')],
        #     [State('threshold_{0}_{1}'.format(self._deviceNumber, self._servoNumber), 'value')]
        # )(dynamically_generated_function)
        pass

    # def __createLockStatusCallback(self, servoNumber):
    #     def callback(n_interval, lockstate, sliderlist, n_submit_threshold, greater, threshold):
    #         context = dash.callback_context
    #         return controller.lockStatus(lockstate, threshold, sliderlist, greater, context, self._deviceNumber, servoNumber)
    #     return callback

    # def __createRelockCallback(self):
    #     def callback(value):
    #         return controller.callAutolockRelock(value, self._deviceNumber, self._servoNumber)
    #     return callback
