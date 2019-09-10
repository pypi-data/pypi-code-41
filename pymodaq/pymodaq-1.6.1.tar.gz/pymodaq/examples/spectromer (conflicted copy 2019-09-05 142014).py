import sys
import tables
from collections import OrderedDict
import datetime
import os
import numpy as np

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QLocale, QDateTime, QRectF, QDate, QThread, Qt

from pyqtgraph.dockarea import Dock
from pymodaq.daq_utils.daq_utils import DockArea

from pyqtgraph.parametertree import Parameter, ParameterTree
import pyqtgraph.parametertree.parameterTypes as pTypes
import pymodaq.daq_utils.custom_parameter_tree as custom_tree
from pymodaq.daq_utils.daq_utils import select_file, Enm2cmrel, Ecmrel2Enm


from pymodaq.daq_viewer.daq_viewer_main import DAQ_Viewer
from pymodaq.daq_move.daq_move_main import DAQ_Move
from pymodaq.daq_utils.plotting.viewer0D.viewer0D_main import Viewer0D
from pymodaq.daq_utils.plotting.viewer1D.viewer1D_main import Viewer1D
from pymodaq.daq_utils.plotting.viewer2D.viewer2D_main import Viewer2D
from pymodaq.daq_utils.h5browser import browse_data
from pymodaq.daq_utils import daq_utils as utils
from pymodaq.daq_utils.h5browser import H5Browser


class Spectrometer(QObject):
    #custom signal that will be fired sometimes. Could be connected to an external object method or an internal method
    log_signal = pyqtSignal(str)

    #list of dicts enabling the settings tree on the user interface
    params_config = [{'title': 'Configuration settings:', 'name': 'config_settings', 'type': 'group', 'children': [
                        {'title': 'Laser wavelength (nm):', 'name': 'laser_wl', 'type': 'int', 'value': 515},
                        {'title': 'List of detectors:', 'name': 'list_detector', 'type': 'list'},
                        {'title': 'Show detector:', 'name': 'show_det', 'type': 'bool', 'value': False},
                        ],
                     }]

    params_acq = [{'title': 'Acquisition settings:', 'name': 'acq_settings', 'type': 'group', 'children': [
                    {'title': 'Center frequency:', 'name': 'center_frequency', 'type': 'float', 'value': 800,},
                    {'title': 'Units:', 'name': 'units', 'type': 'list', 'value': 'nm', 'values': ['nm', 'cm-1']},
                    {'title': 'Exposure (ms):', 'name': 'exposure', 'type': 'float', 'value': 100,},
                    ],
                   },]

    def __init__(self, parent):
        QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
        super().__init__()
        if not isinstance(parent, DockArea):
            raise Exception('no valid parent container, expected a DockArea')

        self.wait_time = 2000 #ms

        self.dockarea = parent
        self.mainwindow = parent.parent()
        self.spectro_widget = QtWidgets.QWidget()

        self.detector_types = [dict(type='DAQ1D', name='Mock'), dict(type='DAQ1D', name='OceanOptics'), dict(type='DAQ1D', name='Shamrock'),
                               dict(type='DAQ1D', name='TCPServer'), dict(type='DAQ2D', name='AndorCCD'),]




        #init the object parameters
        self.detector = None
        self.save_file_pathname = None
        self.center_wavelength = 550
        self.raw_data = []

        #init the user interface
        self.set_GUI()

        dets = [det['name'] for det in self.detector_types]
        self.settings_config.child('config_settings', 'list_detector').setOpts(limits=dets)
        self.settings_config.child('config_settings', 'list_detector').setValue('Mock')
        self.show_detector(False)



    def set_GUI(self):
        ###########################################
        ###########################################
        #init the docks containing the main widgets

        #######################################################################################################################
        #create a dock containing a viewer object, displaying the data for the spectrometer
        self.dock_viewer = Dock('Viewer dock', size=(350, 350))
        self.dockarea.addDock(self.dock_viewer, 'left')
        target_widget = QtWidgets.QWidget()
        self.viewer = Viewer1D(target_widget)
        self.dock_viewer.addWidget(target_widget)

        ###################################################################################
        #create 2 docks to display the DAQ_Viewer (one for its settings, one for its viewer)
        dock_detector_settings = Dock("Detector Settings", size=(350, 350))
        self.dockarea.addDock(dock_detector_settings, 'right')
        dock_detector_settings.float()
        self.detector_area = dock_detector_settings.area
        dock_detector = Dock("Detector Viewer", size=(350, 350))
        self.detector_area.addDock(dock_detector, 'right', dock_detector_settings)
        #init one daq_viewer object named detector
        self.detector = DAQ_Viewer(self.dockarea, dock_settings=dock_detector_settings,
                                                 dock_viewer=dock_detector, title="Spectro Detector", DAQ_type='DAQ1D')
        self.detector.log_signal.connect(self.update_status)
        ################################################################
        #create a logger dock where to store info senf from the programm
        self.dock_logger = Dock("Logger")
        self.logger_list = QtWidgets.QListWidget()
        self.logger_list.setMinimumWidth(300)
        self.dock_logger.addWidget(self.logger_list)
        self.dockarea.addDock(self.dock_logger, 'right')
        self.log_signal[str].connect(self.add_log)


        #############################################


        dock_config_settings = Dock('Configuration', size=(300, 350))
        self.dockarea.addDock(dock_config_settings, 'above', self.dock_logger)
        # create main parameter tree
        self.settings_config_tree = ParameterTree()
        dock_config_settings.addWidget(self.settings_config_tree, 10)
        self.settings_config_tree.setMinimumWidth(300)
        self.settings_config = Parameter.create(name='settings_acq', type='group', children=self.params_config)
        self.settings_config_tree.setParameters(self.settings_config, showTop=False)
        #any change to the tree on the user interface will call the parameter_tree_changed method where all actions will be applied
        self.settings_config.sigTreeStateChanged.connect(self.parameter_tree_changed)

        #this one for the custom application settings
        dock_acq_settings = Dock('Acquisition', size=(300, 350))
        self.dockarea.addDock(dock_acq_settings, 'above', dock_config_settings)
        # create main parameter tree
        self.settings_acq_tree = ParameterTree()
        dock_acq_settings.addWidget(self.settings_acq_tree, 10)
        self.settings_acq_tree.setMinimumWidth(300)
        self.settings_acq = Parameter.create(name='settings_acq', type='group', children=self.params_acq)
        self.settings_acq_tree.setParameters(self.settings_acq, showTop=False)
        #any change to the tree on the user interface will call the parameter_tree_changed method where all actions will be applied
        self.settings_acq.sigTreeStateChanged.connect(self.parameter_tree_changed)






        ############################################
        # creating a menubar
        self.menubar = self.mainwindow.menuBar()
        self.create_menu(self.menubar)

        #creating a toolbar
        self.toolbar = QtWidgets.QToolBar()
        self.create_toolbar()
        self.mainwindow.addToolBar(self.toolbar)

        #creating a status bar
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setMaximumHeight(25)
        self.status_center = custom_tree.SpinBoxCustom()
        self.status_center.setReadOnly(True)
        self.status_center.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.status_center.setMaximumWidth(100)
        self.status_center.setToolTip('center frequency of the spectrum, either in nm or cm-1')

        self.statusbar.addPermanentWidget(self.status_center)
        self.dockarea.window().setStatusBar(self.statusbar)

    def update_status(self,txt,log_type=None):
        """

        """
        self.statusbar.showMessage(txt,self.wait_time)
        if log_type is not None:
            self.log_signal.emit(txt)


    def init_detector(self):

        if self.init_action.isChecked():
            self.statusbar.showMessage('Initializing')
            self.detector.ui.IniDet_pb.click()
            if self.detector.ui.Detector_type_combo.currentText() == 'Mock':
                self.detector.settings.child('main_settings', 'wait_time').setValue(100)
            QtWidgets.QApplication.processEvents()
            QThread.msleep(1000)
            self.detector.grab_done_signal.connect(self.show_data)
            self.statusbar.clearMessage()
        else:
            self.detector.ui.IniDet_pb.click()
            #self.detector.grab_done_signal.disconnect()

    def show_detector(self, show=True):
        self.detector_area.window().setVisible(show)


    def parameter_tree_changed(self, param, changes):
        for param, change, data in changes:
            path = self.settings_acq.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            if change == 'childAdded':
                pass

            elif change == 'value':
                if param.name() == 'list_detector':
                    if data is not None:
                        dets = [det['name'] for det in self.detector_types]
                        ind = dets.index(data)
                        det_type = self.detector_types[ind]['type']
                        self.detector.ui.DAQ_type_combo.setCurrentText(det_type)
                        QtWidgets.QApplication.processEvents()

                        self.detector.ui.Detector_type_combo.setCurrentText(data)

                elif param.name() == 'show_det':
                    self.show_detector(data)



                elif param.name() == 'laser_wl':
                    self.move_laser_wavelength(data)

                elif param.name() == 'center_frequency':
                    unit = self.settings_acq.child('acq_settings', 'units').value()
                    if unit == 'nm':
                        center_wavelength = data
                    elif unit == 'cm-1':
                        center_wavelength = Ecmrel2Enm(data, self.settings_config.child( 'config_settings', 'laser_wl').value())

                    if center_wavelength != self.center_wavelength:
                        self.center_wavelength = center_wavelength
                        self.move_center_wavelength(self.center_wavelength)
                    self.status_center.setSuffix(self.settings_acq.child('acq_settings', 'units').value())
                    self.status_center.setValue(self.settings_acq.child('acq_settings', 'center_frequency').value())

                elif param.name() == 'units':
                    if data == 'nm':
                        self.settings_acq.child('acq_settings', 'center_frequency').setValue(self.center_wavelength)
                    elif data == 'cm-1':
                        self.settings_acq.child('acq_settings', 'center_frequency').setValue(Enm2cmrel(self.center_wavelength,
                                                self.settings_config.child( 'config_settings', 'laser_wl').value()))

                    self.status_center.setSuffix(self.settings_acq.child('acq_settings', 'units').value())
                    self.status_center.setValue(self.settings_acq.child('acq_settings', 'center_frequency').value())


            elif change == 'parent':
                pass

    def move_center_wavelength(self, center_wavelength):
        #do hardware stuff if possible (shamrock, labspec...)
        self.statusbar.showMessage('Moving grating center wavelength', self.wait_time)
        pass

    def move_laser_wavelength(self, laser_wavelength):
        #do hardware stuff if possible (labspec...)
        self.statusbar.showMessage('Moving laser wavelength', self.wait_time)
        pass

    @pyqtSlot(OrderedDict)
    def show_data(self,data):
        """
        do stuff with data from the detector if its grab_done_signal has been connected
        Parameters
        ----------
        data: (OrderedDict) #OrderedDict(name=self.title,x_axis=None,y_axis=None,z_axis=None,data0D=None,data1D=None,data2D=None)
        """
        if 'data1D' in data:
            data1D = [[data['data1D'][key]['data']] for key in data['data1D']]
            self.raw_data = data1D
            self.viewer.show_data(data1D)

    def create_menu(self, menubar):
        """
        """
        menubar.clear()

        #%% create file menu
        file_menu=menubar.addMenu('File')
        load_action=file_menu.addAction('Load file')
        load_action.triggered.connect(self.load_file)
        save_action=file_menu.addAction('Save file')
        save_action.triggered.connect(self.save_data)

        file_menu.addSeparator()
        quit_action=file_menu.addAction('Quit')
        quit_action.triggered.connect(self.quit_function)

        settings_menu=menubar.addMenu('Settings')
        docked_menu=settings_menu.addMenu('Docked windows')
        action_load=docked_menu.addAction('Load Layout')
        action_save=docked_menu.addAction('Save Layout')


    def load_file(self):
        #init the data browser module
        widg = QtWidgets.QWidget()
        self.data_browser = H5Browser(widg)
        widg.show()

    def quit_function(self):
        #close all stuff that need to be
        self.detector.quit_fun()
        QtWidgets.QApplication.processEvents()
        self.mainwindow.close()

    def create_toolbar(self):
        iconquit = QtGui.QIcon()
        iconquit.addPixmap(QtGui.QPixmap(":/icons/Icon_Library/close2.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
        self.quit_action = QtWidgets.QAction(iconquit, "Quit program", None)
        self.toolbar.addAction(self.quit_action)
        self.quit_action.triggered.connect(self.quit_function)

        iconload = QtGui.QIcon()
        iconload.addPixmap(QtGui.QPixmap(":/icons/Icon_Library/Open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadaction = QtWidgets.QAction(iconload, "Load target file (.h5, .png, .jpg) or data from camera", None)
        self.toolbar.addAction(self.loadaction)
        self.loadaction.triggered.connect(self.load_file)


        iconsave = QtGui.QIcon()
        iconsave.addPixmap(QtGui.QPixmap(":/icons/Icon_Library/SaveAs.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
        self.saveaction = QtWidgets.QAction(iconsave, "Save current data", None)
        self.toolbar.addAction(self.saveaction)
        self.saveaction.triggered.connect(self.save_data)

        self.init_action = QtWidgets.QAction("Ini. det", None)
        self.init_action.setCheckable(True)
        self.toolbar.addAction(self.init_action)
        self.init_action.triggered.connect(self.init_detector)

        iconrun = QtGui.QIcon()
        iconrun.addPixmap(QtGui.QPixmap(":/icons/Icon_Library/run2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.grab_action = QtWidgets.QAction(iconrun, 'Grab', None)
        self.grab_action.setCheckable(True)
        self.toolbar.addAction(self.grab_action)
        self.grab_action.triggered.connect(self.grab_detector)

        iconsnap = QtGui.QIcon()
        iconsnap.addPixmap(QtGui.QPixmap(":/icons/Icon_Library/snap.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.snap_action = QtWidgets.QAction(iconsnap, 'Snap', None)
        self.snap_action.triggered.connect(self.snap_detector)
        self.toolbar.addAction(self.snap_action)




    def grab_detector(self):
        self.detector.ui.grab_pb.click()

    def snap_detector(self):
        self.detector.ui.single_pb.click()


    def save_data(self):
        try:
            fname = utils.select_file(start_path=self.save_file_pathname, save=True, ext='h5')

            if not (not (fname)):
                with tables.open_file(str(fname), mode='w', title='an example h5 file name') as h5file:
                    data_to_save = np.squeeze(np.array(self.raw_data))
                    #save metadata
                    h5file.root._v_attrs['settings'] = custom_tree.parameter_to_xml_string(self.settings_acq)
                    for ind in range(data_to_save.shape[1]):
                        arr = h5file.create_array('/', 'data_{:d}'.format(ind), data_to_save[:,ind])
                        arr._v_attrs['shape'] = data_to_save.shape[0]
                        arr._v_attrs['type'] = 'data1D'

                    arr = h5file.create_array('/', 'data_2D', data_to_save)
                    arr._v_attrs['shape'] = data_to_save.shape
                    arr._v_attrs['type'] = 'data2D'



                    logger = "logging"
                    text_atom = tables.atom.ObjectAtom()
                    logger_array = h5file.create_vlarray('/', logger, atom=text_atom)
                    logger_array._v_attrs['type'] = 'list'
                    for ind_log in range(self.logger_list.count()):
                        txt = self.logger_list.item(ind_log).text()
                        logger_array.append(txt)

                st = 'file {:s} has been saved'.format(fname)
                self.add_log(st)
                self.settings_acq.child('min_settings', 'info').setValue(st)


        except Exception as e:
            self.add_log(str(e))


    @pyqtSlot(str)
    def add_log(self, txt):
        """
            Add a log to the logger list from the given text log and the current time

            ================ ========= ======================
            **Parameters**   **Type**   **Description**

             *txt*             string    the log to be added
            ================ ========= ======================

        """
        now = datetime.datetime.now()
        new_item = QtWidgets.QListWidgetItem(str(now) + ": " + txt)
        self.logger_list.addItem(new_item)
        ##to do
        ##self.save_parameters.logger_array.append(str(now)+": "+txt)

    @pyqtSlot(str)
    def emit_log(self, txt):
        """
            Emit a log-signal from the given log index

            =============== ======== =======================
            **Parameters**  **Type** **Description**

             *txt*           string   the log to be emitted
            =============== ======== =======================

        """
        self.log_signal.emit(txt)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QMainWindow()
    area = DockArea()
    win.setCentralWidget(area)
    win.resize(1000, 500)
    win.setWindowTitle('pymodaq example')
    prog = Spectrometer(area)
    win.show()
    sys.exit(app.exec_())