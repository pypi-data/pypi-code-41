#!/usr/bin/env python

import sys
import locale

from PyQt5.QtWidgets import QApplication
from DeclaTravaux.main_window import MainWindow

def main():
    locale.setlocale(locale.LC_ALL, '')

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    rc = app.exec()
    sys.exit(rc)

main()