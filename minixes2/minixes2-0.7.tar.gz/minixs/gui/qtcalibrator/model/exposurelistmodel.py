'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''
from PyQt5.QtCore import QAbstractTableModel, QModelIndex
from PyQt5.QtCore import Qt
from minixs.calibrate import Calibration
import logging
from minixs import METHOD_ENTER_STR
from PyQt5.Qt import QVariant
logger = logging.getLogger(__name__)

TABLE_DATA_OUT_OF_RANGE = "Trying to access data that is out of range"
ENERGY_HEADER = "Incident Energy"
EXPOSURE_HEADER = "Exposure File"
ENERGY_COLUMN_NUMBER = 0
EXPOSURE_COLUMN_NUMBER = 1
TOTAL_COLUMNS = 2

class ExposureListModel(QAbstractTableModel):
    '''
    Model for holding information about the Exposures to be used.  Model part
    of Model/View pattern
    '''


    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        super(ExposureListModel, self).__init__(*args, **kwargs)
        self.modelData = Calibration()
        
    def appendEnergy(self, energy):
        '''
        Append energy value the table.  New energy values are appended
        after the last non empty space in the table.  If there is no 
        space, the list is expanded.
        '''
        count = self.rowCount()
        index = self.findLastEmptyItem(ENERGY_COLUMN_NUMBER)
        
        if index >= count:
            self.insertRow(index, )
        self.setData(self.index(index, ENERGY_COLUMN_NUMBER, self.parent), energy)
        
        
    def appendExposure(self, exposure_file):
        '''
        Append Exposure value to the table.  New values are appended
        after the last non empty space.  If there is no space, the 
        list is expanded.
        '''
        count = self.rowCount()
        index = self.findLastEmptyItem(EXPOSURE_COLUMN_NUMBER)
        
        if index >= count:
            self.insertRow(index, )
        self.setData(self.index(index, EXPOSURE_COLUMN_NUMBER, self.parent), exposure_file)
    
    def columnCount(self, parent=QModelIndex()):
        '''
        Provide column count.  Always 2 Energy and Exposure File
        '''
        return TOTAL_COLUMNS
    
    def data(self, index, role=Qt.DisplayRole):
        '''
        Method to retrieve data from the model.  Data is retrieved by
        index and by role.
        '''
        logger.debug(METHOD_ENTER_STR % ((index.row(), index.column(), role),))
        if not( role == Qt.DisplayRole or role == Qt.EditRole or 
                role == Qt.StatusTipRole):
            return QVariant()
        if index.row() >= self.rowCount():
            logger.exception("Index.row %s >= rowCount %s" % (index.row(), self.rowCount()))
            raise ValueError("%s %s" % \
                             (TABLE_DATA_OUT_OF_RANGE, \
                              (index.row(), index.column)))
        if not index.isValid():
            logger.error("Index not valid")
            return QVariant()
        if role == Qt.DisplayRole or Qt.EditRole:
            if index.column() == ENERGY_COLUMN_NUMBER:
                logger.debug("Reading data for energy(%s) %s" % (index.row(), self.modelData.energies[index.row()]))
                logger.debug("self.modelData.energies %s" % self.modelData.energies)
                return self.tr(str(self.modelData.energies[index.row()]))
            elif index.column() == EXPOSURE_COLUMN_NUMBER:
                logger.debug("Reading data for exposure_files(%s) %s" % (index.row(), self.modelData.exposure_files[index.row()]))
                return self.tr(self.modelData.exposure_files[index.row()])
            else:
                logger.exception("wrong column(%s) for row %s" % (index.row(), index.column()))
                raise ValueError("%s %s" %
                                 (TABLE_DATA_OUT_OF_RANGE, 
                                  (index.row(), index.column)))
        if role == Qt.StatusTipRole:
            return self.tr("Energy: %s, Filename: %s" % 
                           (self.modelData.energies[index.row()], 
                            self.modelData.exposure_files[index.row()]))
    
    def index(self, row, column, parent):
        return self.createIndex(row, column)
    
    def findLastEmptyItem(self, column):
        logger.debug(METHOD_ENTER_STR)
        count = self.rowCount()
        i = count-1;
        logger.debug("rowCount %s" % count)
        while i>=0:
            if column == ENERGY_COLUMN_NUMBER:
                logger.debug("i %s, self.model.energies: %s" %(i, self.modelData.energies))
                if self.modelData.energies[i] != None:
                    break
                i -= 1
            elif column == EXPOSURE_COLUMN_NUMBER:
                if self.modelData.exposure_files[i] != None:
                    break
                i -= 1
        index = i + 1
        logger.debug("Found last item at index %s" % index)
        return index

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        
        if orientation == Qt.Horizontal:
            if section == ENERGY_COLUMN_NUMBER:
                logger.debug("Getting section %s, %s role %s" % (section, ENERGY_HEADER, role))
                return self.tr(ENERGY_HEADER)
            elif section == EXPOSURE_COLUMN_NUMBER:
                logger.debug("Getting section %s, %s role %s" % (section, EXPOSURE_HEADER, role))
                return self.tr(EXPOSURE_HEADER)
        else: 
            return self.tr(str(section))
        
    def insertRows(self, row, count, parent=QModelIndex()):
        logger.debug(METHOD_ENTER_STR % ((row, count),))
        self.beginInsertRows(parent, row, row+count-1)
        for index in range(count):
            self.modelData.energies.insert(row+index, None)
            self.modelData.exposure_files.insert(row+index, None)
        self.endInsertRows()
        return True
        
    def parent(self, index):
        return self.parent
    
    def removeRows(self, row, count, parent=QModelIndex()):
        logger.debug(METHOD_ENTER_STR % ((row, count),))
        self.beginRemoveRows(parent, row, row+count-1)
        for index in range(count):
            self.modelData.energies.remove(self.modelData.energies[index+row])
            self.modelData.exposure_files.remove(\
                                    self.modelData.exposure_files[index+row])
        self.endRemoveRows()
        return True
        
        
    def setData(self, index, value, role=Qt.EditRole):
        logger.debug(METHOD_ENTER_STR % ((index.row(),index.column(), value, role),))
        if index.column() == ENERGY_COLUMN_NUMBER:
            self.modelData.energies[index.row()] = value
            logger.debug("Changing data for energy(%s) %s" %(index.row(), self.modelData.energies[index.row()]))
        elif index.column() == EXPOSURE_COLUMN_NUMBER:
            self.modelData.exposure_files[index.row()] = value
            logger.debug("Changing data for exposure_files(%s) %s" %(index.row(), self.modelData.exposure_files[index.row()]))
        logger.debug("self.modelData.energies %s" % self.modelData.energies)
        self.dataChanged.emit(index, index)
        return True
    
    def rowCount(self, parent=QModelIndex()):
        return max(len(self.modelData.energies), 
                   len(self.modelData.exposure_files))

    
    def setCalibration(self, calibrationModel):
        self.modelData = calibrationModel