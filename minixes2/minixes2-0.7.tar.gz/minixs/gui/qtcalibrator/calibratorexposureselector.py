'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt5.Qt import QPushButton, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout,\
    QDialog, QFileDialog, QWidget, QComboBox, QSpacerItem,\
    QTableWidgetItem, QMessageBox, Qt
from PyQt5.QtCore import pyqtSignal, QModelIndex
from minixs import METHOD_ENTER_STR
from minixs.config.minixsconfigparser import MinixsConfigParser, FILE_SECTION,\
    LAST_DIRECTORY_STR
from minixs.gui.qtcalibrator.model.exposurelistmodel import ExposureListModel,\
    EXPOSURE_COLUMN_NUMBER, ENERGY_COLUMN_NUMBER
from minixs.gui.qtcalibrator.view.exposurelistview import ExposureListView
from os.path import realpath
import logging
import minixs.gui.util
import minixs.misc
import os
from PyQt5.QtWidgets import QDialogButtonBox
logger = logging.getLogger(__name__)

SELECT_ENERGY_TITLE = "Select Energy File"
EMPTY_STR = ""
# Strings used as GUI labels
CANCEL_LABEL = "Cancel"
COLUMN_LABEL = "Column:"
DATASET_NAME_LABEL = "DatasetName: "
DONE_LABEL = "Done"
READ_ENERGIES_LABEL = "Read Energies..."
SELECT_EXPOSURES_LABEL = "Select Exposures..."
APPEND_ROW_LABEL = "AppendRow"
DELETE_ROWS_LABEL = "Delete Row(s)"
CLEAR_ENERGIES_LABEL = "Clear Energies"
CLEAR_EXPOSURES_LABEL = "Clear Exposures"
READ_ENERGY_DIALOG_TITLE = "Open Energy File"
TEXT_FILE_LABEL = "Text File"
# Strings used to name object signals
ENERGIES_LIST_CHANGED_SIGNAL = "exposureListChangedSignal"
EXPOSURE_LIST_CHANGED_SIGNAL = "energiesListChangedSignal"
TABLE_APPEND_ROW_SIGNAL = "tableAppendRow"
TABLE_DELETE_ROWS_SIGNAL = "tableRemoveRows"
CLEAR_ENERGIES_SIGNAL = "clearEnergies"
CLEAR_EXPOSURES_SIGNAL = "clearExposures"

class SelectEnergiesDialog(QDialog):
    '''
    Dialog for selecting file containing energies and selecting which column contains the energies
    '''

    def __init__(self, *args, **kwargs):
        super(SelectEnergiesDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(SELECT_ENERGY_TITLE)
        self.config = MinixsConfigParser()
        self.filename = EMPTY_STR
        vLayout = QVBoxLayout()
        hLayout = QHBoxLayout()
        #ROW 1
        label = QLabel(TEXT_FILE_LABEL)
        self.fileNameTxt = QLineEdit()
        fileButton = QPushButton("...")
        fileButton.clicked.connect(self.onSelectFile)
        self.fileNameTxt.editingFinished.connect(self.onFilenameEditFinished)
        hLayout.addWidget(label)
        hLayout.addWidget(self.fileNameTxt)
        hLayout.addWidget(fileButton)
        vLayout.addLayout(hLayout)
        #ROW 2
        hLayout = QHBoxLayout()
        label = QLabel(COLUMN_LABEL)
        self.columnSelect = QComboBox()
        hLayout.addWidget(label)
        hLayout.addWidget(self.columnSelect)
        vLayout.addLayout(hLayout)
        #ROW 3
        hLayout = QHBoxLayout()
        spacer = QSpacerItem(100, 10)
        hLayout.addItem(spacer)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                   QDialogButtonBox.Cancel, 
                                   Qt.Horizontal,self)
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        vLayout.addWidget(buttons)
        self.setLayout(vLayout)
    
    def cancelSelectEnergies(self):
        logger.debug(METHOD_ENTER_STR)   
        self.finished.emit(self.rejected)

    def doneSelectEnergies(self):
        logger.debug(METHOD_ENTER_STR)
        self.finished.emit(self.accepted)
        
    def onSelectFile(self):
        lastPath = self.config.getLastFilePath()
        filename, _ = QFileDialog.getOpenFileName(None, 
                                        caption=READ_ENERGY_DIALOG_TITLE, 
                                        directory=lastPath)
        logger.debug("Filename %s" % filename)
        self.processNewFilename(filename)

    def onFilenameEditFinished(self,):
        filename = self.fileNameTxt.text()
        file_exists = os.path.isfile(filename)
        if file_exists:
            self.processNewFilename(filename)
        else:
            if filename != "":
                QMessageBox.warning(self, "File %s does not exist" % filename)
             
    def processNewFilename(self, filename):
        if filename != "":
            columns = None
            try:
                columns = minixs.gui.util.read_scan_column_names(filename)
            except IndexError:
                QMessageBox.warning(self, "Error", \
                                    (("Trouble reading %s.  Make sure that " + \
                                    "this is a proper scanFile.") % filename))
                return
            
            if columns:
                self.columnSelect.clear()
                self.columnSelect.addItems(columns)
    
            for col in columns:
                if 'energy' in col.lower():
                    self.columnSelect.setCurrentText(col)
            self.filename = filename
            self.fileNameTxt.setText(self.filename)
            self.config.set(FILE_SECTION, LAST_DIRECTORY_STR, realpath(self.filename))
            self.config.updateFile()
        else:
            pass

        
    def getSelectedColumn(self):
        if self.filename != EMPTY_STR:
            columnData = minixs.misc.read_scan_info(self.filename, \
                            [self.columnSelect.currentIndex()])[0]
            return columnData
        else:
            return []
                
class CalibratorExposureSelector(QWidget):
    '''
    class to set up a table to list energies and image files for doing 
    the energy calibration.
    '''

    exposureListChanged = pyqtSignal(name=EXPOSURE_LIST_CHANGED_SIGNAL)    
    energiesListChanged = pyqtSignal(name=ENERGIES_LIST_CHANGED_SIGNAL)
    tableAppendRow = pyqtSignal(name=TABLE_APPEND_ROW_SIGNAL)
    tableDeleteRows = pyqtSignal(list, name=TABLE_DELETE_ROWS_SIGNAL)
    clearExposures = pyqtSignal(name=CLEAR_EXPOSURES_SIGNAL)
    clearEnergies = pyqtSignal(name=CLEAR_ENERGIES_SIGNAL)
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CalibratorExposureSelector, self).__init__(parent)
        self.config = MinixsConfigParser()
        
        vLayout = QVBoxLayout()
        hLayout = QHBoxLayout()
        label = QLabel(DATASET_NAME_LABEL)
        self.datasetNameTxt = QLineEdit()
        hLayout.addWidget(label)
        hLayout.addWidget(self.datasetNameTxt)
        vLayout.addLayout(hLayout)
        self.model = None
        
        hLayout = QHBoxLayout()
        
        self.tableView = ExposureListView()
        hLayout.addWidget(self.tableView)
        
        buttonLayout = QVBoxLayout()
        
        self.readEnergiesButton = QPushButton(READ_ENERGIES_LABEL)
        self.selectExposuresButton = QPushButton(SELECT_EXPOSURES_LABEL)
        self.appendRowButton = QPushButton(APPEND_ROW_LABEL)
        self.deleteRowsButton = QPushButton(DELETE_ROWS_LABEL)
        self.clearEnergiesButton = QPushButton(CLEAR_ENERGIES_LABEL)
        self.clearExposuresButton = QPushButton(CLEAR_EXPOSURES_LABEL)
        self.selectExposuresButton.setEnabled(False)
        self.deleteRowsButton.setEnabled(False)
        self.clearEnergiesButton.setEnabled(False)
        self.clearExposuresButton.setEnabled(False)
        buttonLayout.addWidget(self.readEnergiesButton)
        buttonLayout.addWidget(self.selectExposuresButton)
        buttonLayout.addWidget(self.appendRowButton)
        buttonLayout.addWidget(self.deleteRowsButton)
        buttonLayout.addWidget(self.clearEnergiesButton)
        buttonLayout.addWidget(self.clearExposuresButton)
        
        hLayout.addLayout(buttonLayout)
        vLayout.addLayout(hLayout)
        self.setLayout(vLayout)
        
        self.readEnergiesButton.clicked.connect(self.onReadEnergies)
        self.selectExposuresButton.clicked.connect(self.onSelectExposures)
        self.appendRowButton.clicked.connect(self.onAppendRow)
        self.deleteRowsButton.clicked.connect(self.onDeleteRows)
        self.clearEnergiesButton.clicked.connect(self.onClearEnergies)
        self.clearExposuresButton.clicked.connect(self.onClearExposures)

    def appendRows(self, energies, filenames):
#         self.tableView.model().setRowCount(len(energies))
        row = 0
        for energy, filename in zip(energies, filenames):
            self.tableView.model().appendEnergy(energy)
            self.tableView.model().appendExposure(filename)
            row += 1
        self.exposureListChanged.emit()
       
#     def getExposureList(self):
#         exposures = []
#         for row in range(self.tableView.model().rowCount()):
#             expName = str(self.tableView.model().item(row, 1).text())
#             if expName == EMPTY_STR:
#                 logger.debug("item contains empty string")
#             exposures.append(expName)
#         return exposures
#             
    def onReadEnergies(self):
        '''
        Method for signal to read Energies
        '''
        logger.debug(METHOD_ENTER_STR)
        energySelectDialog = SelectEnergiesDialog()
        status = energySelectDialog.exec_()
#         status = energySelectDialog.result()
        logger.debug ("Energy Select Dialog Status %s" % status)
        #logger.debug("energySelector Accepted: %s" % energySelectDialog.accepted())
        if status == QDialog.Rejected:
            return
        selectedEnergies =  energySelectDialog.getSelectedColumn()
        logger.debug("selectedEnergies %s" % (selectedEnergies,))
        if len(selectedEnergies) == 0:            # No Energies were loaded
            pass
        else:
            for energy in selectedEnergies:
                self.tableView.model().appendEnergy(energy)
            
        if (self.tableView.model().rowCount() > 0):
            self.selectExposuresButton.setEnabled(True)
            self.deleteRowsButton.setEnabled(True)
            self.clearEnergiesButton.setEnabled(True)
            self.clearExposuresButton.setEnabled(True)
            self.energiesListChanged.emit()
        else:
            self.selectExposuresButton.setEnabled(False)
            self.deleteRowsButton.setEnabled(False)
            self.clearEnergiesButton.setEnabled(False)
            self.clearExposuresButton.setEnabled(False)
    
    def onSelectExposures(self):
        '''
        Method for signal to select exposures
        '''
        logger.debug(METHOD_ENTER_STR)
        lastPath = self.config.getLastFilePath()
        filenames, _ = QFileDialog.getOpenFileNames(None, 
                                         caption=READ_ENERGY_DIALOG_TITLE, 
                                         directory=lastPath)
        logger.debug("Filename %s" % (filenames,))
        if len(filenames) == 0:
            return
        for exposureFile in filenames:
            self.tableView.model().appendExposure(exposureFile)
            
        self.exposureListChanged.emit()
        
    def onAppendRow(self):
        '''
        Method to append a row
        '''
        logger.debug(METHOD_ENTER_STR)
        rowCount = self.tableView.model().rowCount()
#         self.tableView.model().setRowCount(rowCount+1)
        self.tableView.model().insertRow(rowCount)
        if self.tableView.model().rowCount() > 0:
            self.deleteRowsButton.setEnabled(True)
        else:
            self.deleteRowsButton.setEnabled(False)
        self.tableAppendRow.emit()
        
    def onDeleteRows(self):
        '''
        Method to delete rows
        '''
        logger.error(METHOD_ENTER_STR)
        # Append 
        selectedIndexes = self.tableView.selectedIndexes()
        logger.debug("selectedRanges %s" % selectedIndexes)
        selectedRows = set()
        for index in selectedIndexes:
            selectedRows.add(index.row())
        if len(selectedRows) > 0:
            selectedRows = list(selectedRows)
            selectedRows.sort(reverse=True)
        else:
            return
        for row in selectedRows:
            logger.debug("Removing Row %s" % row)
            self.tableView.model().removeRow(row)
        logger.debug("# of rows %s" % self.tableView.model().rowCount())
        if self.tableView.model().rowCount() > 0:
            self.deleteRowsButton.setEnabled(True)
        else:
            self.deleteRowsButton.setEnabled(False)
        self.tableDeleteRows.emit(selectedRows)
        
        
    def onClearEnergies(self):
        '''
        method to clear energies
        '''
        logger.debug(METHOD_ENTER_STR)
        for row in range(self.tableView.model().rowCount()):
            index = self.tableView.model().index(row, ENERGY_COLUMN_NUMBER, QModelIndex())
            self.tableView.model().setData(index, None)
        self.clearEnergies.emit()
        
    def onClearExposures(self):
        '''
        method to clear exposure list
        '''
        logger.debug(METHOD_ENTER_STR)
        for row in range(self.tableView.model().rowCount()):
            index = self.tableView.model().index(row, EXPOSURE_COLUMN_NUMBER,QModelIndex())
            self.tableView.model().setData(index, None)
        
        self.clearExposures.emit()
        
    def getData(self):
        '''
        retrieve data from the table for energies and filenames, if there is 
        a matching filename for each energy then return True for valid,
        otherwise return false for Valid
        
        '''
        energies = []
        files = []
        valid = True
        fileName = ""
        energy = ""
        for row in range(self.tableView.model().rowCount()):
            index = self.tableView.model().index(row, ENERGY_COLUMN_NUMBER, QModelIndex())
            energyItem = self.tableView.model().data(index)
            logger.debug("energyItem %s" % energyItem)
            logger.debug(type("energyItem) %s" % type(energyItem) ))
            logger.debug("energyItem is None '%s'" % (energyItem is None))
            logger.debug("len(energyItem) %s" % (len(energyItem)))
            logger.debug("dir(energyItem %s" % dir(energyItem))
            logger.debug("energyItem is None %s" % (energyItem == ''))
            if energyItem is None or energyItem =='None':
                energy = None
            else:
                energy = float(energyItem)
            index = self.tableView.model().index(row, EXPOSURE_COLUMN_NUMBER, QModelIndex())
            fileItem = self.tableView.model().data(index)
            logger.debug("fileItem %s"  % fileItem)
            if fileItem is None or str(fileItem)=='':
                fileName = None
            else:
                fileName = str(fileItem)
            if energy == None and fileName == None:
                continue
            if energy == None or fileName==None:
                valid = False
                continue
            energies.append(float(energy))
            files.append(fileName)
        return (valid, energies, files)
    
    def setButtonsForNoExposures(self):
        '''
        Set buttons on right side for the case that no exposures have been selected.
        '''
        self.selectExposuresButton.setEnabled(True)
        self.deleteRowsButton.setEnabled(True)
        self.clearEnergiesButton.setEnabled(True)
        self.clearExposuresButton.setEnabled(True)
        self.energiesListChanged.emit()
    
    def setButtonsForExposures(self):
        '''
        Set buttons on the right side for the case that images have been added.
        '''
        self.selectExposuresButton.setEnabled(True)
        self.deleteRowsButton.setEnabled(True)
        self.clearEnergiesButton.setEnabled(True)
        self.clearExposuresButton.setEnabled(True)
        self.energiesListChanged.emit()
        
    def setCalibrationModel(self, calibrationModel):
        self.calibrationModel = calibrationModel
        self.exposureListModel = ExposureListModel()
        self.exposureListModel.setCalibration(self.calibrationModel)
        self.tableView.setModel(self.exposureListModel)
        