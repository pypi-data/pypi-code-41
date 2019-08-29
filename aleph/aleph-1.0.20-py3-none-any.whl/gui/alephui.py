#! /usr/bin/env python3
from PySide2 import QtWidgets, QtCore, QtGui
import sys, os, json, glob, shutil

from ui_aleph import Ui_Aleph
from settings import Settings

MAX_FOLDERS = 30

class Aleph(QtWidgets.QMainWindow):
	def __init__(self, MainWindow):
		super().__init__()

		QtCore.QCoreApplication.setOrganizationName("ALEPH");
		QtCore.QCoreApplication.setApplicationName("ALEPH");
		self.settings = QtCore.QSettings()
		self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"img/icon.png")))
		self.init_settings()
		self.set_point_size()
		self.ui = Ui_Aleph()
		self.ui.setupUI(self)
		self.ui.paintMainWindow()

		self.set_project_directory(os.getcwd())
		self.init_ui()

		self.infoFile = "info.json"
		self.outputFile = "output.json"

	def init_ui(self):
		self.ui.actionMenu.triggered.connect(lambda: self.switch_page(0))
		self.ui.libraryButton.clicked.connect(lambda: self.switch_page(1))
		self.ui.decompositionButton.clicked.connect(lambda: self.switch_page(2))
		self.ui.superpositionButton.clicked.connect(lambda: self.switch_page(3))
		self.ui.annotationButton.clicked.connect(lambda: self.switch_page(4))
		self.ui.actionSettings.triggered.connect(self.settings_aleph)
		self.ui.actionOpen.triggered.connect(self.open_aleph)
		self.ui.runButton.clicked.connect(self.run_aleph)
		self.ui.actionSave.triggered.connect(self.save_aleph)
		self.general_aspects_line()

	def init_settings(self):
		#If the settings are not in QSettings (.config/IBMB/ALEPH.conf)
		#we need to initialize them

		alephPath = self.settings.value("aleph_path")
		if alephPath == "" or alephPath == None:
			self.settings.setValue("aleph_path","ALEPH")
		cootPath = self.settings.value("coot_path")
		if cootPath == "" or cootPath == None:
			self.settings.setValue("coot_path","coot")
		peptideLength = self.settings.value("peptide_length")
		if peptideLength == None:
			self.settings.setValue("peptide_length",3)
		sampling = self.settings.value("sampling")
		if sampling == None:
			self.settings.setValue("sampling","none")
		maxAhDist = self.settings.value("max_ah_dist")
		if maxAhDist == None:
			self.settings.setValue("max_ah_dist",20)
		minAhDist = self.settings.value("min_ah_dist")
		if minAhDist == None:
			self.settings.setValue("min_ah_dist",0)
		maxBsDist = self.settings.value("max_bs_dist")
		if maxBsDist == None:
			self.settings.setValue("max_bs_dist",15)
		minBsDist = self.settings.value("min_bs_dist")
		if minBsDist == None:
			self.settings.setValue("min_bs_dist",0)
		cycles = self.settings.value("cycles")
		if cycles == None:
			self.settings.setValue("cycles",15)
		deep = self.settings.value("deep")
		if deep == None:
			self.settings.setValue("deep",0)
		topn = self.settings.value("topn")
		if topn == None:
			self.settings.setValue("topn",4)
		writeGraphml = self.settings.value("write_graphml")
		if writeGraphml == None:
			self.settings.setValue("write_graphml",0)
		widthPic = self.settings.value("width_pic")
		if widthPic == None:
			self.settings.setValue("width_pic",100)
		heightPic = self.settings.value("height_pic")
		if heightPic == None:
			self.settings.setValue("height_pic",20)
		fontSize = self.settings.value("font_size")
		if fontSize == None:
			self.settings.setValue("font_size",10)
		color = self.settings.value("color")
		if color == None:
			self.settings.setValue("color","yellow")

	def switch_page(self, page):
		if page == 0:
			self.ui.actionMenu.setEnabled(False)
			self.ui.actionSave.setEnabled(False)
			if not self.ui.actionStop.isEnabled():
				self.ui.actionRun.setEnabled(False)
		else:
			self.ui.actionMenu.setEnabled(True)
			self.ui.actionSave.setEnabled(True)
			if not self.ui.actionStop.isEnabled():
				self.ui.actionRun.setEnabled(True)
	
		self.ui.stackedWidget.setCurrentIndex(page)

	def set_project_directory(self, path):
		self.projectDir = path
		self.ui.statusBar.showMessage("Current directory: "+path)
		os.chdir(path)
		self.ui.annotation.set_project_directory(path)
		self.ui.decomposition.set_project_directory(path)
		self.ui.library.set_project_directory(path)
		self.ui.superposition.set_project_directory(path)

	def open_aleph(self):
		path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select a directory:", "", QtWidgets.QFileDialog.ShowDirsOnly)
		if path:
			self.set_project_directory(path)

	def run_aleph(self):
		index = self.ui.stackedWidget.currentIndex()
		if index == 1:
			self.ui.library.run_library()
		elif index == 2:
			self.ui.decomposition.run_decomposition()
		elif index == 3:
			self.ui.superposition.run_superposition()
		elif index == 4:
			self.ui.annotation.run_annotation()

	def test_aleph(self):
		index = self.ui.stackedWidget.currentIndex()
		if index == 1:
			self.ui.library.test_library()

	def take_screenshot(self, browser):
		left = 0
		top = 0
		width = browser.width()
		height = browser.height()
		image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
		rg = QtGui.QRegion(left, top, width, height)
		painter = QtGui.QPainter(image)
		browser.page().view().render(painter, QtCore.QPoint(), rg)
		painter.end()

		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None,"Save screenshot as", self.projectDir, "PNG (*.png)", "PNG (*.png)")
		if fileName:
			try:
				image.save(fileName,"PNG",80)
			except OSError as e:
				errorDialog = QtWidgets.QErrorMessage()
				errorDialog.showMessage(str(e))
				errorDialog.exec()

	def save_aleph(self):
		index = self.ui.stackedWidget.currentIndex()
		if index == 1:
			item = self.ui.library.ui.tree.currentIndex()
			path = self.ui.library.ui.model.filePath(item)
		elif index == 2:
			item = self.ui.decomposition.ui.tree.currentIndex()
			path = self.ui.decomposition.ui.model.filePath(item)
		elif index == 3:
			item = self.ui.superposition.ui.tree.currentIndex()
			path = self.ui.superposition.ui.model.filePath(item)
		elif index == 4:
			item = self.ui.annotation.ui.tree.currentIndex()
			path = self.ui.annotation.ui.model.filePath(item)
			
		if ".pdb" in path:
			options = QtWidgets.QFileDialog.Options()
			fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None,"Save As", self.projectDir,"", options=options)
			if fileName:
				try:
					shutil.copy2(path,fileName)
				except OSError as e:
					errorDialog = QtWidgets.QErrorMessage()
					errorDialog.showMessage(str(e))
					errorDialog.exec()

	def finished_aleph(self):
		if self.ui.stackedWidget.currentIndex() != 0:
			self.ui.actionRun.setEnabled(True)
		self.ui.actionStop.setEnabled(False)

	def started_aleph(self):
		self.ui.actionRun.setEnabled(False)
		self.ui.actionStop.setEnabled(True)

	def settings_aleph(self):
		dialog = Settings()
		dialog.exec_()
		self.general_aspects_line()
		self.set_point_size()
		self.ui.paintMainWindow()

	def general_aspects_line(self):
		#Creat he general aspects line, it is the same for all the programs
		self.generalAspects = " --peptide_length "+str(self.settings.value("peptide_length"))\
		+ " --width_pic "+str(self.settings.value("width_pic"))\
		+ " --height_pic "+str(self.settings.value("height_pic"))\
		+ " --min_ah_dist "+str(self.settings.value("min_ah_dist"))\
		+ " --max_ah_dist "+str(self.settings.value("max_ah_dist"))\
		+ " --min_bs_dist "+str(self.settings.value("min_bs_dist"))\
		+ " --max_bs_dist "+str(self.settings.value("max_bs_dist"))

		if int(self.settings.value("write_graphml")) == 2:
			self.generalAspects += " --write_graphml"

	def set_point_size(self):
		app = QtWidgets.QApplication.instance()
		font = app.font()
		size = self.settings.value("font_size")
		font.setPointSize(int(size))
		app.setFont(font)

	def remove_folder(self, path, model):
		folders = list(filter(os.path.isdir, glob.glob(path + "/*")))
		folders.sort(key=lambda x: os.path.getmtime(x))
		if len(folders) > MAX_FOLDERS:
			try:
				deletePath = folders[0]
				#first we have to clean the folder
				#necessary in order to not get a system watcher error
				for file in os.scandir(deletePath):
					if os.path.isfile(file.path):
						os.unlink(file.path)
					elif os.path.isdir(file.path): 
						shutil.rmtree(file.path)
				#delete just the folder through filesystemmodel
				index = model.index(deletePath,0)
				model.rmdir(index)
			except OSError:
				pass

	def run_dialog(self, line, path, data, widget):
		self.runDialog = QtWidgets.QDialog()
		self.runDialog.setObjectName("RunAleph")
		self.runDialog.setWindowTitle("ALEPH RUN")
		self.runDialog.resize(700, 150)
		self.runDialog.gridLayout = QtWidgets.QGridLayout(self.runDialog)
		self.runDialog.gridLayout.setObjectName("gridLayout")

		self.runDialog.label = QtWidgets.QLabel(self.runDialog)
		self.runDialog.label.setObjectName("label")
		self.runDialog.label.setText("ALEPH run command:")
		self.runDialog.gridLayout.addWidget(self.runDialog.label, 0, 0, 1, 1)		
		self.runDialog.textRun = QtWidgets.QTextEdit(self.runDialog)
		self.runDialog.textRun.setObjectName("textRun")
		self.runDialog.textRun.setText(line)
		self.runDialog.gridLayout.addWidget(self.runDialog.textRun, 1, 0, 1, 1)
		self.runDialog.buttonBox = QtWidgets.QDialogButtonBox(self.runDialog)
		self.runDialog.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
		self.runDialog.buttonBox.setObjectName("buttonBox")
		self.runDialog.gridLayout.addWidget(self.runDialog.buttonBox)
		self.runDialog.buttonBox.accepted.connect(lambda: self.run_accepted(path, data, widget))
		self.runDialog.buttonBox.rejected.connect(self.run_rejected)
		self.runDialog.exec_()

	def run_accepted(self, path, data, widget):

		i = 0
		aux = data["title"]
		while os.path.exists(os.path.join(path, aux)):
			i += 1
			aux = data["title"]+"_"+str(i)
		widget.runPath = os.path.join(path, aux)
		os.makedirs(widget.runPath, exist_ok=True)
		index = widget.ui.model.index(widget.runPath)
		widget.ui.tree.setExpanded(index, True)
		widget.show_list()
		with open(os.path.join(widget.runPath, self.infoFile), "w+") as file:
			json.dump(data, file)
		self.remove_folder(path, widget.ui.model)

		self.process = QtCore.QProcess(self)
		self.process.setWorkingDirectory(widget.runPath)
		self.process.setStandardOutputFile(widget.runPath+"/log.txt")
		self.process.finished.connect(widget.on_finish)
		self.process.finished.connect(self.finished_aleph)
		self.process.started.connect(self.started_aleph)
		self.ui.stopButton.clicked.connect(self.process.kill)
		print(self.runDialog.textRun.toPlainText())
		self.process.start(self.runDialog.textRun.toPlainText())
		self.runDialog.close()

	def run_rejected(self):
		self.runDialog.close()

	def check_connection(self):
		hostname = "www.ebi.ac.uk"
		response = os.system("ping -c 1 " + hostname + " > /dev/null 2>&1")
		if response == 0:
		  return True
		else:
		  return False

def main():
	sys.argv.append("--disable-web-security")
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle("fusion")
	MainWindow = QtWidgets.QMainWindow()
	window = Aleph(MainWindow)
	window.showMaximized()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
