'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import logging
from PyQt5.QtCore import pyqtSignal, pyqtSlot
logger = logging.getLogger(__name__)


LABEL_NAME_STR = 'labelName'
ITEM_LIST_STR = 'itemList'

class FilterView(qtWidgets.QWidget):
    '''
    classdocs
    '''

    filterChanged = pyqtSignal(object, name="filterChanged")
    
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        self.layout = qtWidgets.QHBoxLayout()
        self.labelName = None
        self.valueWidget = None
        if (LABEL_NAME_STR in kwargs):
            self.labelName = kwargs[LABEL_NAME_STR]
            del kwargs[LABEL_NAME_STR]
        if 'filter' in kwargs.keys():
            self.filter = kwargs['filter']
            del(kwargs['filter'])
        super(FilterView, self).__init__(*args, **kwargs)
        self.enableBox = qtWidgets.QCheckBox(self.filter.name)
        self.layout.addWidget(self.enableBox)
        self.setLayout(self.layout)
        self.enableBox.clicked.connect(self.filterEnableChanged)
        
    def setValue(self, value):
        pass 
    
    def getValue(self):
        return None

    def isEnabled(self):
        return self.enableBox.isEnabled()
    
    def text(self):
        return self.enableBox.text()
    
    def filterEnabled(self):
        return self.enableBox.isChecked()
    
    def filterEnableChanged(self, enabled):
        self.valueWidget.setEnabled(enabled)
        self.filterChanged.emit(self)
        
class IntFilterView(FilterView):
    
    def __init__(self, *args, **kwargs):
        super(IntFilterView, self).__init__(*args, **kwargs)
        self.valueWidget = qtWidgets.QSpinBox()
        self.layout.addWidget(self.valueWidget)
        self.valueWidget.setMaximum(10000000)
        self.valueWidget.setValue(self.filter.default_val)
        self.valueWidget.setEnabled(self.filter.default_enabled)
        self.enableBox.setChecked(self.filter.default_enabled)
        self.valueWidget.valueChanged.connect(self.handleValueChanged)
        
    def setValue(self, value):
        self.valueWidget.setValue(value)
    
    def getValue(self):
        return self.valueWidget.value()
    
    @pyqtSlot(int)
    def handleValueChanged(self, value):
        self.filterChanged.emit(self)
        
class StringFilterView(FilterView):
    
    def __init__(self, *args, **kwargs):
        super(StringFilterView, self).__init__(*args, **kwargs)
        self.valueWidget = qtWidgets.QLineEdit()
        self.layout.addWidget(self.valueWidget)
        self.valueWidget.setText(self.filter.default_val)
        self.valueWidget.setEnabled(self.filter.default_enabled)
        self.enableBox.setChecked(self.filter.default_enabled)
        self.valueWidget.editingFinished.connect(self.handleValueChanged)

    def setValue(self, value):
        self.valueWidget.setText(value)
        
    def getValue(self):
        return self.valueWidget.text()

    @pyqtSlot()
    def handleValueChanged(self):
        self.filterChanged.emit(self)
        
    
class ChoiceFilterView(FilterView):
    
    def __init__(self, * args, **kwargs):
#         if (ITEM_LIST_STR in kwargs):
#             self.labelName = kwargs[ITEM_LIST_STR]
#             del kwargs[ITEM_LIST_STR]
        super(ChoiceFilterView, self).__init__(*args, **kwargs)
        self.valueWidget = qtWidgets.QComboBox()
        logger.debug("Choices %s" % self.filter.CHOICES)
        #for choice in self.filter.CHOICES:
        self.valueWidget.addItems(self.filter.CHOICES)
        self.layout.addWidget(self.valueWidget)
#        self.valueWidget.setCurrentIndex(self.filter.default_val[0])
        self.valueWidget.setEnabled(self.filter.default_enabled)
        self.valueWidget.setCurrentIndex(0)
        self.enableBox.setChecked(self.filter.default_enabled)
        
        self.valueWidget.currentIndexChanged.connect(self.handleValueChanged)

    def setValue(self, value):
        self.valueWidget.setCurrentIndex(value)

    def getValue(self):
        return self.valueWidget.currentText()
        
    @pyqtSlot(int)
    def handleValueChanged(self, selectionIndex):
        self.filterChanged.emit(self)
        
        
REGISTRY = []

def register(fltr, view):
  global REGISTRY
  REGISTRY.append((fltr, view)) #, wx.NewId()

def filter_ids():
  global REGISTRY
  return [id for flter, view in REGISTRY] #, id
