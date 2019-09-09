'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
from os.path import realpath
import traceback

from PyQt5.Qt import pyqtSlot, QFileDialog, QProgressBar
from PyQt5.QtWidgets import QAction, QMessageBox
from pyqtgraph.graphicsItems.ViewBox.ViewBox import ViewBox

import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets
from minixs import METHOD_ENTER_STR, filetype
from minixs.calibrate import Calibration
from minixs.config.minixsconfigparser import MinixsConfigParser, FILE_SECTION, \
    LAST_DIRECTORY_STR
from minixs.exposure import Exposure
from minixs.filetype import InvalidFileError
from minixs.filter import get_filter_by_name
from minixs.gui import util
from minixs.gui.qtcalibrator.ImageViewQt import ImageViewQt
from minixs.gui.qtcalibrator.calibratorexposureselector import CalibratorExposureSelector
from minixs.gui.qthelpers.wildcards import WILDCARD_CALIB, WILDCARD_XTAL, \
    WILDCARD_XTAL_EXPORT
from minixs.misc import find_xtal_boundaries
import numpy as np
from PyQt5.QtCore import QCoreApplication

try:
    from itertools import izip as zip     # Python 2 way, For python 3 can use zip directly
except ImportError:
    pass                                  # Nothing to do for python 3
logger = logging.getLogger(__name__)

APP_NAME = "Calibrator"
SAVE_CALIB_TITLE = "Save Calibration File"
OPEN_CALIB_TITLE = "Open Calibration File"
EXPORT_XTAL_TITLE = "Export Crystal Boundaries"
IMPORT_XTAL_TITLE = "Import Crystal Boundaries"
INVALID_FILE_TEXT = "Invalid file"
INVALID_FILE_TYPE_TEXT = "Invalid file type"


class CalibrationModel(Calibration):
    def __init__(self):
        super(CalibrationModel, self).__init__()

class CalibratorMainWindow(qtWidgets.QMainWindow):
    '''
    Defines the main window for the Calibrator
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CalibratorMainWindow, self).__init__(parent)
        
        self.model = CalibrationModel()
        self.config = MinixsConfigParser()
        self.createMenuBar()
        
        self.splitter = qtWidgets.QSplitter(qtCore.Qt.Vertical)
        self.exposureSelector = CalibratorExposureSelector()
        self.exposureSelector.setCalibrationModel(self.model)
        self.exposureSelector.exposureListChanged.connect(self.handleExposureListChanged)
        self.exposureSelector.energiesListChanged.connect(self.handleEnergiesListChanged)
        self.exposureSelector.tableAppendRow.connect(self.handleTableAppendRow)
        self.exposureSelector.tableDeleteRows[list].connect(self.handleTableDeleteRows)
        self.exposureSelector.clearEnergies.connect(self.handleClearEnergies)
        self.exposureSelector.clearExposures.connect(self.handleClearExposures)
        self.exposureSelector.tableView.singleEnergyChanged[int, float].connect(self.handleSingleEnergyChanged)
        self.exposureSelector.tableView.singleExposureNameChanged[int, str].connect(self.handleSingleExposureNameChanged)
        self.splitter.addWidget(self.exposureSelector)
        self.imageView = ImageViewQt()
        self.imageView.findCrystals.connect(self.handleFindCrystals)
        self.imageView.calibrateButton.clicked.connect(self.handleCalibrate)
        self.imageView.filters.filterChanged.connect(self.handleFilterChanged)
        self.imageView.filters.dispersiveDirection.currentIndexChanged[int].connect(self.handleDispersiveDirectionChanged)
        self.splitter.addWidget(self.imageView)
        
        self.setCentralWidget(self.splitter)
        self.setWindowTitle(APP_NAME)
        statusBar = self.statusBar()
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setMaximumSize(300, 20)
        statusBar.addPermanentWidget(self.progressBar, stretch = 25)
        self.changed = False
        self.calibrationValid(False)

    def Changed(self, changed=True):
        self.changed = changed
        
    def calibrationValid(self, valid):
        self.calibration_valid = valid
        self.imageView.calibrateButton.setEnabled(not valid)
        
    def createMenuBar(self):
        '''
        '''
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        viewMenu = mainMenu.addMenu('&View')
        
        loadCalibAction = QAction("&Open...", self)
        saveCalibAction = QAction("&Save...", self)
        importXtalAction = QAction("&Import Crystals...", self)
        exportXtalAction = QAction("&Export Crystals...", self)
        fileMenu.addAction(loadCalibAction)
        fileMenu.addAction(saveCalibAction)
        fileMenu.addSeparator()
        fileMenu.addAction(importXtalAction)
        fileMenu.addAction(exportXtalAction)
        viewFitPointsAction = QAction("&Fit Points", self, checkable=True)
        viewMenu.addAction(viewFitPointsAction)
        loadCalibAction.triggered.connect(self.loadCalibration)
        saveCalibAction.triggered.connect(self.saveCalibration)
        importXtalAction.triggered.connect(self.importXtals)
        exportXtalAction.triggered.connect(self.exportXtals)
        viewFitPointsAction.triggered.connect(self.handleViewFitPoints)

    @pyqtSlot()
    def exportXtals(self):
        logger.debug(METHOD_ENTER_STR)
        lastPath = self.config.getLastFilePath()
        filename, _ = QFileDialog.getSaveFileName(self, EXPORT_XTAL_TITLE,
                                                   lastPath,
                                                   filter=WILDCARD_XTAL_EXPORT)
        self.viewToModel()
        if (filename != "") and (filename is not None):
            with open(filename, 'w') as f:
                f.write("# miniXS crystal boundaries\n")
                f.write("# x1\ty1\tx2\ty2\n")
                for (x1,y1),(x2,y2) in self.model.xtals:
                    f.write("%d\t%d\t%d\t%d\n" % (x1,y1,x2,y2))
        
#     def handleExposuresDeleted(self):
#         self.setButtonsNoExposures()
        
    def handleCalibrate(self):
        '''
        Activate the calibration method to add the calibration to the model.  
        Check and make sure we have what we need like havig images and defined
        ROIs where calibration should be calculated.
        '''
        logger.debug(METHOD_ENTER_STR)
        self.progressBar.setValue(0)
        self.viewToModel()
        valid, errors = self.validate()
        if not valid:
            errors = [ '% 2d) %s' % (i+1, err) for i, err in enumerate(errors) ]
            message = 'The following must be fixed before calibrating:\n\n' + '\n\n'.join(errors)
            QMessageBox.warning(self, "Calibration Warning", message)
            self.calibration_invalid = True
            return
        self.statusBar().showMessage('Calibrating...  Please Wait')
        
        try:
            self.model.calibrate(progressUpdater=self.progress_updater)
        except Exception as ex:
            tb = traceback.extract_stack()
            tb_string = ""
            logger.debug(tb)
            for f, line, m, stm in tb:
                part = "file %s,  Line: %d, method: %s\n statement: %s\n" % (f, line, m, stm)
                logger.debug("part %s" % part)
                tb_string.join(part)
            logger.debug("tb_string %s" % tb_string)
            QMessageBox.critical(self, "Error", "Error While calibrating\n %s %s" % (ex, tb_string))
            logger.exception(ex)
            return
        self.imageView.matrixView.setImage(self.model.calibration_matrix)
        logger.info("rms_res %s, lin_res %s" % (self.model.rms_res, self.model.lin_res))
        self.imageView.tools.calibrationRadioButton.setChecked(True)
        self.statusBar().showMessage("Done Calibrating")
        self.calibrationValid(True)
        self.Changed()
    
    @pyqtSlot(int)
    def handleDispersiveDirectionChanged(self, direction):
        self.model.dispersive_direction = direction
        self.calibrationValid(False)
        self.Changed()
    
    def handleExposureListChanged(self):
        logger.debug(METHOD_ENTER_STR)
        valid, exposureEnergies, exposureNames = self.exposureSelector.getData()
        self.imageView.loadImages(exposureNames, exposureEnergies)
        logger.debug("Filenames %s" % ((exposureNames, exposureEnergies),))
        self.calibrationValid(False)
        self.Changed()
        
    def handleEnergiesListChanged(self):
        logger.debug(METHOD_ENTER_STR)
        self.calibrationValid(False)
        self.Changed()
        
    def handleFilterChanged(self):
        self.calibrationValid(False)
        
    def handleFindCrystals(self):
        logger.debug(METHOD_ENTER_STR)
        self.viewToModel()
        
        if not self.model.exposure_files:
            return
        
        self.statusBar().showMessage("Finding Boundaries... Please Wait")
        
        exposures = [Exposure(f) for f in self.model.exposure_files]
        for exposure, energy in zip(exposures, self.model.energies):
            exposure.apply_filters(energy, self.model.filters)
            
        xtals = find_xtal_boundaries(exposures)
        
        logger.debug("Crystal boundaries %s" % ((xtals,)))
        
        if xtals is None:
            message = 'Unable to determine boundaries. It may help to increase the low cutoff value.'
            errdlg = QMessageBox.error(self, "Error", message)
            errdlg.ShowModal()
            errdlg.Destroy()
        else:
            self.model.xtals = xtals
            self.imageView.tools.rects = self.model.xtals
#           self.view.imageView.Refresh()
            self.Changed()
            self.calibrationValid(False)
        self.imageView.imageView.addROIs(xtals)

    def handleShowCrystals(self):
        pass

    def handleTableAppendRow(self):
        logger.debug(METHOD_ENTER_STR)
        
    def handleTableDeleteRows(self, rows):
        logger.debug(METHOD_ENTER_STR % (rows,))
        self.imageView.deleteImages(rows)
        valid, exposureEnergies, exposureNames = self.exposureSelector.getData()
        self.imageView.loadImages(exposureNames, exposureEnergies)
        logger.debug("Filenames %s" % ((exposureNames, exposureEnergies),))
        self.calibrationValid(False)
        self.Changed()
        
    def handleClearEnergies(self):
        logger.debug(METHOD_ENTER_STR)
        
    def handleClearExposures(self):
        logger.debug(METHOD_ENTER_STR)
        self.imageView.imageView.deleteAllImages()
    
    def handleSingleEnergyChanged(self, row, energy):
        logger.debug(METHOD_ENTER_STR  % ((row, energy),))
        valid, exposureEnergies, exposureNames = self.exposureSelector.getData()
        self.imageView.loadImages(exposureNames, exposureEnergies)
        logger.debug("Filenames %s" % ((exposureNames, exposureEnergies),))
        self.calibrationValid(False)
        self.Changed()
        
    def handleSingleExposureNameChanged(self, row, exposureName):
        logger.debug(METHOD_ENTER_STR  % ((row, exposureName),))
        valid, exposureEnergies, exposureNames = self.exposureSelector.getData()
        self.imageView.loadImages(exposureNames, exposureEnergies)
        logger.debug("Filenames %s" % ((exposureNames, exposureEnergies),))
        self.calibrationValid(False)
        self.Changed()

    
    @pyqtSlot(bool)
    def handleViewFitPoints(self, checkState=True):
        logger.debug(METHOD_ENTER_STR, checkState)
        self.viewToModel()
        if checkState:
            self.imageView.imageView.viewBox.addItem( self.imageView.imageView.fitPointsView)
            self.imageView.imageView.fitPointsView.setVisible(True)
            self.model.loadFitPoints()
            logger.debug("fit_points %s" % self.model.fit_points)
            self.imageView.imageView.fitPointsView.setData(x=self.model.fit_points[:,0], y=self.model.fit_points[:,1])
            
        else:
            self.imageView.imageView.viewBox.removeItem(self.imageView.imageView.fitPointsView)
            self.imageView.imageView.fitPointsView.setVisible(False)
        
    @pyqtSlot()
    def loadCalibration(self):
        '''
        Load a saved calibration from file
        '''
        logger.debug(METHOD_ENTER_STR)
        lastFilePath = self.config.getLastFilePath()
        filename, _ = QFileDialog.getOpenFileName(self, OPEN_CALIB_TITLE, 
                                                  lastFilePath,
                                                  filter=WILDCARD_CALIB)
        filename = str(filename)
        if filename != "" and (not filename is None):
            try:
                success = self.model.load(filename)
                if not success:
                    errDlg = QMessageBox()
                    errDlg.setText(("Warning: some errors were encountered while " +
                                    " loading the calibration file:\n\n  %s") \
                                     % '\n  '.join(self.model.load_errors))
                    errDlg.setIcon(QMessageBox.Critical)
                    errDlg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
                    
                    retVal = errDlg.exec_()
                    return
            except InvalidFileError as ex:
                errDlg = QMessageBox()
                errDlg.setText(("Warning: some errors were encountered while " +
                                " loading the calibration file:\n\n  %s") \
                                 % '\n  '.join(self.model.load_errors))
                errDlg.setIcon(QMessageBox.Critical)
                errDlg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
                
                retVal = errDlg.exec_()
                return
        else:
            return
                
        self.modelToView()
        
        
    @pyqtSlot()
    def importXtals(self):
        logger.debug(METHOD_ENTER_STR)
        lastPath = self.config.getLastFilePath()
        filename, _ = QFileDialog().getOpenFileName(self, IMPORT_XTAL_TITLE, 
                                                    lastPath,
                                                    filter=WILDCARD_XTAL)
        if filename != "" and filename is not None:
            error = None
            t = filetype.determine_filetype(filename)
            if t == filetype.FILE_CALIBRATION:
                ci = Calibration()
                ci.load(filename, header_only=True)
                self.model.xtals = ci.xtals
            elif t == filetype.FILE_XTALS or t == filetype.FILE_UNKNOWN:
                data = None
                try:
                    data = np.loadtxt(filename)
                    self.model.xtals = [[[x1,y1],[x2,y2]] for x1, y1, x2, y2 in data]
                except ValueError:
                    if data is not None:
                        if len(data.shape) == 1:
                            num = data.shape[0]
                        else:
                            num = data.shape1
                        if num !=4:
                            error = "Crystal file must contain 4 columns"
                        else:
                            error = INVALID_FILE_TEXT
                            
                    else:
                        error = INVALID_FILE_TEXT
            else:
                error = INVALID_FILE_TYPE_TEXT
                
            if error:
                QMessageBox.critical(self, "Error", "Invalid Xtal File")
            self.imageView.imageView.replaceXtals(self.model.xtals)
            self.calibrationValid(False)
            self.Changed()
        
    def modelToView(self):
        logger.debug(METHOD_ENTER_STR)
        self.exposureSelector.datasetNameTxt.setText(self.model.dataset_name)
        self.imageView.filters.dispersiveDirection.setCurrentIndex(self.model.dispersive_direction)
        
        self.exposureSelector.clearExposuresButton.click()
        self.exposureSelector.clearEnergiesButton.click()
        
        self.exposureSelector.appendRows(self.model.energies, self.model.exposure_files)
        
        self.imageView.filters.setFilters(self.model.filters)
        
        self.imageView.imageView.addROIs(self.model.xtals)
        self.imageView.matrixView.setImage(self.model.calibration_matrix)
        
    def progress_updater(self, progressPercent=0):
        logger.debug(METHOD_ENTER_STR % progressPercent)
        self.progressBar.setValue(progressPercent)
        QCoreApplication.processEvents()
        
        
    def validate(self):
        errors = []
        valid = True
    
        if not self.exposure_list_valid:
            valid = False
            errors.append("The exposure list is invalid. Make sure that each row contains an energy and an exposure filename.")
    
        if len(self.model.energies) < 2:
            valid = False
            errors.append("At least two calibration exposures are required for calibration. A larger number of exposures will give a better fit.")
    
        if len(self.model.xtals) < 1:
            valid = False
            errors.append("Define the boundary of at least one crystal.")
    
        intersecting = False
        for xa in self.model.xtals:
            if intersecting:
                break
    
            for xb in self.model.xtals:
                if xa == xb:
                    continue
                if util.xtals_intersect(xa, xb):
                    valid = False
                    errors.append("Crystal boundaries may not overlap.")
                    intersecting = True
                    break
    
        return valid, errors

    @pyqtSlot()
    def saveCalibration(self):
        logger.debug(METHOD_ENTER_STR)
        header_only = False
        if self.calibration_valid == False:
            errDlg = QMessageBox()
            errDlg.setIcon(QMessageBox.Warning)
            errDlg.setText( 
                    "Warning: You have changed parameters since last " +
                    "calibrating. Saving now will only save the " +
                    "parameters, and not the matrix itself.")
            errDlg.StandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            
            retVal = errDlg.exec_()
            if retVal == QMessageBox.Ok:
                logger.debug("Warning box passed OK, saving header only")
                header_only=True
            else:
                return
        lastPath = self.config.getLastFilePath()
        filename, _ = QFileDialog.getSaveFileName(self, SAVE_CALIB_TITLE, 
                                                  lastPath,
                                                  filter=WILDCARD_CALIB )

        if (filename != "") and (not filename is None):
            self.viewToModel()
            self.model.save(filename, header_only=header_only)
        #save last used directory back to the config
        self.config.set(FILE_SECTION, LAST_DIRECTORY_STR, realpath(filename))
        self.config.updateFile()
            
    def viewToModel(self):
        self.model.dataset_name = str(self.exposureSelector.datasetNameTxt.text())
        self.model.dispersive_direction = self.imageView.filters.dispersiveDirection.currentIndex()
        logger.debug("Dispersive Direction %s " % self.model.dispersive_direction)
        # get Energies and exposures
        valid, energies, exposure_files = self.exposureSelector.getData()
        self.exposure_list_valid = valid
        self.model.energies = energies
        self.model.exposure_files = exposure_files
        
        self.model.filters = []
        filters = self.imageView.filters.getFilters()
        for (name, enabled, val) in filters:
            if enabled:
                fltr = get_filter_by_name(name)
                fltr.set_val(val)
                self.model.filters.append(fltr)
        if len(self.imageView.imageView.rois) >0:
            dir (self.imageView.imageView.rois[0].pos())        
        self.model.xtals = [
            [[int(round(roi.pos().x())), int(round(roi.pos().y()))], \
             [int(round(roi.pos().x() + roi.size().x())), int(round(roi.pos().y() + roi.size().y()))]] \
                 for roi in self.imageView.imageView.rois
            ]
     
