'''
Created on May 17, 2019

@author: hammonds
'''
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QTableView
import sys
from minixs.gui.qtcalibrator.model.exposurelistmodel import ExposureListModel
from minixs.gui.qtcalibrator.view.exposurelistview import ExposureListView

class CalibrationTestWindow(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(CalibrationTestWindow, self).__init__( *args, **kwargs)
        self.splitter = QSplitter()
        
        self.tableView = ExposureListView()
        self.model = ExposureListModel()
        self.tableView.setModel(self.model)
        self.model.modelData.energies.append(3)
        self.splitter.addWidget(self.tableView)
        self.tableView2 = QTableView()
        self.tableView2.setModel(self.model)
        self.splitter.addWidget(self.tableView2)
        
        self.setCentralWidget(self.splitter)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = CalibrationTestWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    