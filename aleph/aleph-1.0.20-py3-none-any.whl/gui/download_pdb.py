from PySide2 import QtWidgets, QtCore, QtGui
import os

class DownloadPdb(QtWidgets.QWizard):
	def __init__(self):
		super().__init__()
		self.addPage(DownloadPdb1(self))
		self.addPage(DownloadPdb2(self))		
		self.setObjectName("DownloadPdb")
		self.setWindowTitle("Download PDB")
		self.resize(700, 300)
		self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"img/icon.png")))

		self.directory = ""

	def get_directory(self):
		return self.directory

class DownloadPdb1(QtWidgets.QWizardPage):
	def __init__(self, parent):
		super().__init__()
		self.downloadPdb1Layout = QtWidgets.QGridLayout(self)
		self.downloadPdb1Layout.setObjectName("downloadPdb1Layout")
		self.dirLabel = QtWidgets.QLabel(self)
		self.dirLabel.setObjectName("dirLabel")
		self.dirLabel.setText("Destination directory")
		self.downloadPdb1Layout.addWidget(self.dirLabel, 0, 0, 1, 1)
		self.dirLine = QtWidgets.QLineEdit(self)
		self.dirLine.setObjectName("dirLine")
		self.downloadPdb1Layout.addWidget(self.dirLine, 0, 1, 1, 1)
		self.dirLoad = QtWidgets.QPushButton(self)
		self.dirLoad.setObjectName("dirLoad")
		self.dirLoad.setText("Browse")
		self.downloadPdb1Layout.addWidget(self.dirLoad, 0, 2, 1, 1)

		QtWidgets.QWizardPage.registerField(self, "directory*", self.dirLine);
		
		self.dirLoad.clicked.connect(self.select_directory)
		
	def select_directory(self):
		options = QtWidgets.QFileDialog.Options()
		dirName = QtWidgets.QFileDialog.getExistingDirectory(self, "Select destination directory")
		if dirName:
			self.dirLine.setText(dirName)


class DownloadPdb2(QtWidgets.QWizardPage):
	def __init__(self, parent):
		super().__init__()
		self.downloadPdb2Layout = QtWidgets.QGridLayout(self)
		self.downloadPdb2Layout.setObjectName("downloadPdb2Layout")
		self.commandLabel = QtWidgets.QLabel(self)
		self.commandLabel.setObjectName("dirLabel")
		self.commandLabel.setText("Command")
		self.downloadPdb2Layout.addWidget(self.commandLabel, 0, 0, 1, 1)
		self.commandLine = QtWidgets.QLineEdit(self)
		self.commandLine.setObjectName("dirLine")
		self.downloadPdb2Layout.addWidget(self.commandLine, 0, 1, 1, 1)
		self.commandRun = QtWidgets.QPushButton(self)
		self.commandRun.setObjectName("commandRun")
		self.commandRun.setText("Run")
		self.downloadPdb2Layout.addWidget(self.commandRun, 0, 2, 1, 1)
		self.commandStop = QtWidgets.QPushButton(self)
		self.commandStop.setObjectName("commandRun")
		self.commandStop.setText("Stop")
		self.commandStop.setEnabled(False)
		self.downloadPdb2Layout.addWidget(self.commandStop, 0, 3, 1, 1)
		self.output = QtWidgets.QPlainTextEdit(self)
		self.output.setObjectName("output")
		self.downloadPdb2Layout.addWidget(self.output, 1, 0, 1, 4)
		self.commandRun.clicked.connect(self.command_run)

		self.parent = parent

	def initializePage(self):
		dirLine = QtWidgets.QWizardPage.field(self,"directory");
		command = "rsync -rLptvz --port=33444 rsync.rcsb.org::ftp_data/structures/all/pdb/ " +dirLine
		self.commandLine.setText(command)
		self.commandLine.setCursorPosition(0)
		self.finished = 0

	def command_run(self):
		msg = QtWidgets.QMessageBox()
		msg.setIcon(QtWidgets.QMessageBox.Warning)
		msg.setText("The downloaded pdb can take up to 30GB")
		msg.setStandardButtons(QtWidgets.QMessageBox.Ok  | QtWidgets.QMessageBox.Cancel)
		msg.setWindowTitle("Warning")
		ret = msg.exec_()

		if ret == QtWidgets.QMessageBox.Ok:
			self.process = QtCore.QProcess(self)
			self.process.finished.connect(self.on_finish)
			self.process.readyReadStandardOutput.connect(self.stdout_ready)
			self.process.readyReadStandardError.connect(self.stderr_ready)
			self.process.errorOccurred.connect(self.error_found)
			self.commandStop.setEnabled(True)
			self.commandRun.setEnabled(False)
			self.commandStop.clicked.connect(self.process.kill)
			self.output.appendPlainText(self.commandLine.text())
			self.process.start(self.commandLine.text())

	def on_finish(self, exitCode, exitStatus):
		if exitCode == 0 and exitStatus == 0:
			self.commandStop.setEnabled(False)
			self.commandRun.setEnabled(True)
			self.finished = 1
			self.parent.directory = QtWidgets.QWizardPage.field(self,"directory");
			self.completeChanged.emit()

	def stdout_ready(self):
		text = str(self.process.readAllStandardOutput(), 'utf-8')
		self.output.appendPlainText(text)

	def stderr_ready(self):
		text = str(self.process.readAllStandardError(), 'utf-8')
		self.output.appendPlainText(text)

	def error_found(self, exitCode):
		self.commandStop.setEnabled(False)
		self.commandRun.setEnabled(True)
		if exitCode != 1:
			self.output.appendPlainText("Error has been found")
		
	def isComplete(self):
		return self.finished


