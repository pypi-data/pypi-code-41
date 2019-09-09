'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''
import sys
import PyQt5.QtWidgets as qtWidgets
from minixs.gui.qtcalibrator.calibratormainwindow import CalibratorMainWindow
from minixs import filter
from minixs.gui.qthelpers import qtfilterview
        
def main():
  
    for f in filter.REGISTRY:
        if hasattr(f, 'view_name'):
            view_class = getattr(qtfilterview, f.view_name)
            qtfilterview.register(f, view_class)
            
    
    # Start the app.    
    app = qtWidgets.QApplication(sys.argv)
    mainWindow = CalibratorMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())