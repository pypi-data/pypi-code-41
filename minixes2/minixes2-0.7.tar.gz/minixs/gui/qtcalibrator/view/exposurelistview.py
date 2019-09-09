'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''
from PyQt5.QtWidgets import QTableView, QAbstractItemView, \
    QStyledItemDelegate, QLineEdit
from PyQt5.QtCore import pyqtSignal

import logging
from PyQt5.QtGui import QDoubleValidator
from minixs.gui.qtcalibrator.model.exposurelistmodel import \
    ENERGY_COLUMN_NUMBER, EXPOSURE_COLUMN_NUMBER
from minixs import METHOD_ENTER_STR

logger=logging.getLogger(__name__)

ENERGY_ITEM_CHANGED_SIGNAL = "energyItemChanged"
EXPOSURE_FILE_NAME_CHANGED_SIGNAL = "exposureFilenameChanged"
SINGLE_EXPOSURE_NAME_CHANGED_SIGNAL = "singleExposureNameChanged"
SINGLE_ENERGY_CHANGED_SIGNAL = "singleEnergyChanged"


class ExposureItemDelegate(QStyledItemDelegate):
    '''
    Item Delegate used by the ExposureListView.  This provides for 
    speciql hansling of the information displayed.  
    Special cases handled:
        Column 0 is Energy, which is a real number.  IO for this is 
        QLineEdit with a QDoubleValidator applied.  This validator 
        allows only entry of Real numbers
        Column 1 is Filename of an exposure File.  IO for this is a 
        QLineEdit. Nothing special for this but maybe later could verify 
        valid files
    '''
    energyItemChanged = pyqtSignal(int, float, \
                                   name=ENERGY_ITEM_CHANGED_SIGNAL)
    exposureFileNameChanged = pyqtSignal(int, str, \
                                name=EXPOSURE_FILE_NAME_CHANGED_SIGNAL)
    def __init__(self, parent=None):
        super(ExposureItemDelegate, self).__init__(parent)
        self.parent = parent
        self.index = None
        
    def createEditor(self, parent, option, index):
        '''
        Implementation of the createEditor method for QItemDelegate
        '''
        logger.debug(METHOD_ENTER_STR)
        self.index = index
#         editor = QStyledItemDelegate.createEditor(self, parent, option, index)
        editor = QLineEdit(parent)
        if isinstance(editor, QLineEdit) and index.column() == \
                                                ENERGY_COLUMN_NUMBER:
            logger.debug("Using Energy instance")
            editor.setValidator(QDoubleValidator())
            editor.editingFinished.connect(self.handleFinishedEnergyInput)
        if isinstance(editor, QLineEdit) and index.column() == \
                                                EXPOSURE_COLUMN_NUMBER:
            logger.debug("Using Exposure File instance")
            editor.editingFinished.connect(self.handleFinishedExposureFileInput)
        return editor
    
    def handleFinishedEnergyInput(self):
        '''
        Handle input for Energy entries
        '''
        logger.debug(METHOD_ENTER_STR)
        editor = self.sender()
        logger.debug("senderIndex %s" % self.index.row())
        self.energyItemChanged.emit(self.index.row(), \
                                    float(editor.text()))
        
        
    def handleFinishedExposureFileInput(self):
        '''
        Handle input for ExposureFileEntries
        '''
        logger.debug(METHOD_ENTER_STR)
        editor = self.sender()
        self.exposureFileNameChanged.emit(self.index.row(), \
                                          editor.text())
        

class ExposureListView(QTableView):
    
    '''
    TableView for the list of Energies and exposures
    '''
    # Create signals created by this View
    singleExposureNameChanged = pyqtSignal(int, str, 
                               name=SINGLE_EXPOSURE_NAME_CHANGED_SIGNAL)
    singleEnergyChanged = pyqtSignal(int, float,
                               name=SINGLE_ENERGY_CHANGED_SIGNAL)

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        super(ExposureListView, self).__init__(*args, **kwargs)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.setColumnWidth(1, 500)
        self.setMinimumWidth(600)
        self.setItemDelegate(ExposureItemDelegate())
        self.exposureItemDelegate = ExposureItemDelegate(self)
        self.exposureItemDelegate.energyItemChanged[int, float].connect(self.handleEnergyDelegateChanged)
        self.exposureItemDelegate.exposureFileNameChanged[int,str].connect(self.handleExposureFileNameDelegateChanged)
        self.setItemDelegate(self.exposureItemDelegate)
    
    def handleEnergyDelegateChanged(self, row, energy):
        '''
        Handle signals for the Energy Columns.  This allows manual entry 
        or edit of the info
        '''
        logger.debug(METHOD_ENTER_STR %  ((row, energy),))
        self.singleEnergyChanged.emit(row, energy)
        
    def handleExposureFileNameDelegateChanged(self, row, name):
        '''Handle Signals for the Exposure Files.  This allows manual 
        entry or edit of the info
        
        '''
        logger.debug(METHOD_ENTER_STR %((row, name),))
        self.singleExposureNameChanged.emit(row, name)
        
class ExposureControlView(QAbstractItemView):
    
    
    def __init__(self, *args, **kwargs):
        super(ExposureControlView, self).__init__(*args, **kwargs)
        
