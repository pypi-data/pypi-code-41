from .GUI_Main import *
from PyQt5.QtWidgets import QApplication
import sys
import qdarkstyle

app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
GRID()
app.exec_()
