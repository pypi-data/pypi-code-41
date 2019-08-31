from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton, QFileDialog, QComboBox
from .TSListWidget import TSListWidget
from .AndroidExportCSV import AndroidExportCSV
from .iOSExportCSV import iOSExportCSV
from .WiFiExportCSV import WiFiExportCSV
from .LPCertReport import LPCertReport
import os

class LPCertReportView(QMainWindow):
    def __init__(self):
        super(LPCertReportView, self).__init__()
        self.setWindowTitle = "Linkplay MSP Check Tool"
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.platform = "iOS"

    def display(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        logLabel = QLabel("Log:")
        grid.addWidget(logLabel, 1, 0)

        self.logNameEdit = QLineEdit("")
        self.logNameEdit.setDisabled(True)
        grid.addWidget(self.logNameEdit, 1, 1)

        browseButton = QPushButton("Browse")
        browseButton.clicked.connect(self.openFileNameDialog)
        grid.addWidget(browseButton, 1, 2)

        typeLabel = QLabel("Platform:")
        grid.addWidget(typeLabel, 2, 0, 1, 1)

        self.comboBox = QComboBox()
        self.comboBox.addItem("iOS")
        self.comboBox.addItem("Android")
        self.comboBox.addItem("WiFi")
        self.comboBox.currentIndexChanged.connect(self.comboBoxSelectionChanged)
        grid.addWidget(self.comboBox, 2, 1, 1, 1)

        consoleLabel = QLabel("Console:")
        grid.addWidget(consoleLabel, 3, 0)

        self.resultList = TSListWidget()
        self.resultList.itemClicked.connect(self.resultList.Cliecked)
        self.resultList.show()
        grid.addWidget(self.resultList, 4, 0, 1, 3)
        self.centralWidget.setLayout(grid)

        checkButton = QPushButton("Check")
        checkButton.clicked.connect(self.check)
        grid.addWidget(checkButton, 5, 2)

    def comboBoxSelectionChanged(self, i):
        self.platform = self.comboBox.currentText()
        print(self.platform)

    def logger(self, log):
        print(log)
        self.resultList.addItem(log)

    def createTempDir(self):
        path = "Temp"
        if os.path.exists(path):
            return
        os.mkdir(path)

    # 1. 生成表格
    # 2. 进行Report检查
    @pyqtSlot()
    def check(self):

        self.createTempDir()

        filePath = self.logNameEdit.text()
        if len(filePath) == 0:
            return
        if self.platform == "iOS":
            iosExport = iOSExportCSV(filePath)
            events = iosExport.catchLog()
            path = iosExport.exportReport(events)
        elif self.platform == "Android":
            androidExport = AndroidExportCSV(filePath)
            events = androidExport.catchLog()
            path = androidExport.exportReport(events)
        elif self.platform == "WiFi":
            wifiExport = WiFiExportCSV(filePath)
            events = wifiExport.catchLog()
            path = wifiExport.exportReport(events)

        if len(path) > 0:
            certReport = LPCertReport(path, self.platform, self.logger)
            certReport.readXlsx()
            certReport.startParse()


    @pyqtSlot()
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        self.logNameEdit.setText(fileName)

def main():
    app = QApplication([])
    w = QMainWindow()
    certUI = LPCertReportView()
    certUI.display()
    certUI.resize(600, 600)
    certUI.show()

    app.exec_()


if __name__ == "__main__":
    main()

