from PySide2 import QtWidgets, QtCore
from ui_decomposition import Ui_Decomposition
import os, glob, json, re

class Decomposition(QtWidgets.QWidget):
	def __init__(self, parent):   
		super().__init__(parent)
		self.parent = parent
		self.decompositionPath = ""
		self.defaultNameRun = "run"
		self.ui = Ui_Decomposition()
		self.ui.setupUI(self)
		self.init_ui()

	def set_project_directory(self, path):
		self.decompositionPath = os.path.join(path,"aleph_decomposition")
		self.show_list()	

	def init_ui(self):
		self.ui.pdbLoad.clicked.connect(self.load_pdb)
		self.ui.saveButton.clicked.connect(self.take_screenshot)
		self.ui.alphaSlider.valueChanged.connect(lambda: self.value_change("alpha"))
		self.ui.betaSlider.valueChanged.connect(lambda: self.value_change("beta"))
		self.ui.tree.clicked.connect(self.item_selected)
		self.ui.representationValue.currentTextChanged.connect(self.representation_change)
		self.ui.numberValue.valueChanged.connect(self.change_number)
		self.ui.templateCheck.stateChanged.connect(self.template_check)
		self.ui.templateValue.currentTextChanged.connect(self.template_change)
		self.ui.iterativeCheck.stateChanged.connect(self.disable_algorithm)

	def run_decomposition(self):
		settings = QtCore.QSettings()
		alephPath = settings.value("aleph_path")
		titleInput = re.sub('[ /:]', '', self.ui.titleLine.text())
		pdbInput = self.ui.pdbLine.text()
		alphaInput = str(float(self.ui.alphaSlider.value()/100))
		betaInput = str(float(self.ui.betaSlider.value()/100))
		homogeneityInput = self.ui.homogeinityCheck.isChecked()
		packInput = self.ui.packCheck.isChecked()
		algorithmInput = self.ui.algorithmValue.currentText()
		iterativeInput = self.ui.iterativeCheck.isChecked()
		if titleInput == "":
			titleInput = nameRun = re.sub('[ /:]', '', os.path.splitext(os.path.basename(pdbInput))[0])

		line = alephPath
		if iterativeInput:
			line += " find_folds"
		else:
			line += " decompose --algorithm "+algorithmInput

		line += " --pdbmodel "+pdbInput+" --strictness_ah "+alphaInput+" --strictness_bs "+betaInput
		line += " "+self.parent.generalAspects
		
		if homogeneityInput:
			line += " --homogeneity"
		if packInput:
			line += " --pack_beta_sheet"

		data = { "title": titleInput, "pdb": pdbInput, "alpha": alphaInput, "beta": betaInput,\
				"algorithm": algorithmInput, "homogeneity": homogeneityInput, "pack": packInput, "iterative": iterativeInput }		
		self.parent.run_dialog(line, self.decompositionPath, data, self)

	def item_selected(self, item):
		#when we select an item in the qtreeview
		if item.isValid():
			path = self.ui.model.filePath(item)
			if ".pdb" in path:
				formattedPath = os.path.dirname(os.path.relpath(path, self.decompositionPath))
				with open(os.path.join(self.decompositionPath,formattedPath, self.parent.infoFile), "r") as file:
					data = json.load(file)
					self.ui.titleLine.setText(data["title"])
					self.ui.pdbLine.setText(data["pdb"])
					self.ui.alphaSlider.setValue(float(data["alpha"])*100)
					self.ui.betaSlider.setValue(float(data["beta"])*100)
					self.ui.algorithmValue.setCurrentText(data["algorithm"])
					self.ui.homogeinityCheck.setChecked(data["homogeneity"])
					self.ui.packCheck.setChecked(data["pack"])
					self.ui.iterativeCheck.setChecked(data["iterative"])

					if data["iterative"] is True:
						self.ui.numberValue.setEnabled(True)
						self.update_number(item.data())
					else:
						self.ui.numberValue.setEnabled(False)
				self.show_pdb(path)

	def take_screenshot(self):
		self.parent.take_screenshot(self.ui.browser)

	def update_number(self, pdbName):
		number = re.match((r"^.*\_(\d*)\_.*$"), pdbName)
		if "input_search.pdb" not in pdbName and number is not None:
			self.ui.numberValue.blockSignals(True)
			self.ui.numberValue.setValue(int(number.group(1)))
			self.ui.numberValue.blockSignals(False)

	def disable_algorithm(self, state):
		if state != 0:
			self.ui.algorithmValue.setEnabled(False)
		else:
			self.ui.algorithmValue.setEnabled(True)

	def template_check(self, state):
		self.item_selected(self.ui.tree.currentIndex())

	def template_change(self):
		if self.ui.templateCheck.isChecked():
			self.item_selected(self.ui.tree.currentIndex())

	def representation_change(self, which):
		self.item_selected(self.ui.tree.currentIndex())

	def change_number(self, value):
		index = self.ui.tree.currentIndex()
		if index.data() is not None:
			pdbName = index.data()
			parentFolder = index.parent().data()
			number = re.match((r"^.*\_(\d*)\_.*$"), pdbName)
			if "input_search.pdb" not in pdbName and number is not None:
				replace = "_"+str(number.group(1))+"_"
				newList = pdbName.rsplit(replace, 1)
				new = ("_"+str(value)+"_").join(newList)
				newPath = os.path.join(self.decompositionPath,parentFolder, new)
				index = self.ui.model.index(newPath,0)
				if index.data() is not None:
					self.ui.tree.setCurrentIndex(index)
					self.show_pdb(newPath)


	def on_finish(self, exitCode, exitStatus):
		if exitCode == 0 and exitStatus == 0:
			searchPdb = glob.glob(os.path.join(self.runPath,"*.pdb"))
			for pdb in searchPdb:
				if "distclust" in pdb:
					index = self.ui.model.index(pdb,0)
					self.ui.tree.setCurrentIndex(index)
					self.item_selected(index)
					break
		else:
			if exitCode != 9:
				errorDialog = QtWidgets.QMessageBox()
				errorDialog.setWindowTitle("ERROR")
				errorDialog.setIcon(QtWidgets.QMessageBox.Critical)
				errorDialog.setText(self.parent.process.readAllStandardError().data().decode('utf8'))
				errorDialog.exec()

	def load_pdb(self):
		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select PDB File", "","PDB File *.pdb *.ent", options=options)
		if fileName:
			self.ui.pdbLine.setText(fileName)

	def value_change(self, which):
		if which == "alpha":
			value = float(self.ui.alphaSlider.value()/100)
			self.ui.alphaValue.setText("{:.2f}".format(value).replace(".",","))
		else:
			value = float(self.ui.betaSlider.value()/100)
			self.ui.betaValue.setText("{:.2f}".format(value).replace(".",","))

	def show_list(self):
		#Show the new folder
		if os.path.exists(self.decompositionPath):
			self.ui.tree.showColumn(0)
			self.ui.tree.showColumn(3)
			self.ui.tree.setRootIndex(self.ui.model.setRootPath(self.decompositionPath))
		else:
			self.ui.tree.hideColumn(0)
			self.ui.tree.hideColumn(3)

	def show_pdb(self, pdbPath):
		#Load the .hmtl in /dist/ngl.html and replace the fields with the new parameters
		htmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.html"))
		with open(htmlPath , "r+") as file:
			html = file.read()

		settings = QtCore.QSettings()
		templateColor = settings.value("color")
		
		jsPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.js"))
		jsLocalPath = QtCore.QUrl.fromLocalFile(jsPath)
		pdbLocalPath = QtCore.QUrl.fromLocalFile(pdbPath)

		pdbRep = ""

		if self.ui.templateCheck.isChecked() and os.path.exists(self.ui.pdbLine.text()):
			fileLocalPath = QtCore.QUrl.fromLocalFile(self.ui.pdbLine.text())
			pdbRep = "stage.loadFile(\""+fileLocalPath.toString()+"\").then(function (o) {\
        					o.addRepresentation(\""+self.ui.templateValue.currentText()+"\", {color:\""+templateColor+"\"});});"

		pdbRep += "stage.loadFile(\""+pdbLocalPath.toString()+"\").then(function (o) { o.addRepresentation(\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"chainid\"});stage.autoView();});"
		
		html = html.replace("JS", jsLocalPath.toString())
		html = html.replace("ADDINPUT", pdbRep)

		self.ui.browser.setHtml(html)