from PySide2 import QtWidgets, QtCore
from ui_superposition import Ui_Superposition
import os, glob, json, re

class Superposition(QtWidgets.QWidget):
	def __init__(self, parent):   
		super().__init__(parent)
		self.parent = parent
		self.superpositionPath = ""
		self.defaultNameRun = "run"
		self.ui = Ui_Superposition()
		self.ui.setupUI(self)
		self.init_ui()
		self.pdbs = []
		self.target = []
		self.reference = False

	def set_project_directory(self, path):
		self.superpositionPath = os.path.join(path,"aleph_superposition")
		self.show_list()

	def init_ui(self):
		self.ui.referenceLoad.clicked.connect(self.load_reference)
		self.ui.fragmentLoad.clicked.connect(self.load_fragment)
		self.ui.fragmentDirLoad.clicked.connect(self.load_fragment_dir)
		self.ui.tree.clicked.connect(self.item_selected)
		self.ui.representationValue.currentTextChanged.connect(self.representation_change)
		self.ui.colorValue.currentTextChanged.connect(self.color_change)
		self.ui.representationReferenceValue.currentTextChanged.connect(self.representation_reference_change)
		self.ui.colorReferenceValue.currentTextChanged.connect(self.color_reference_change)
		self.ui.saveButton.clicked.connect(self.take_screenshot)
		self.ui.saveButton2.clicked.connect(self.take_screenshot2)

	def run_superposition(self):
		settings = QtCore.QSettings()
		alephPath = settings.value("aleph_path")
		titleInput = re.sub('[ /:]', '', self.ui.titleLine.text())
		pdbInput = self.ui.referenceLine.text()
		fragmentInput = self.ui.fragmentLine.text()
		fragmentCheckInput = self.ui.fragmentRadio.isChecked()
		dirInput = self.ui.fragmentDirLine.text()
		intraInput = str(self.ui.intraSpin.value())
		interInput = str(self.ui.interSpin.value())		
		rmsdInput = self.ui.rmsdValue.value()
		superposeInput = self.ui.superposeCheck.isChecked()

		if titleInput == "":
			titleInput = re.sub('[ /:]', '', os.path.splitext(os.path.basename(pdbInput))[0])

		line = alephPath+" superpose --reference "+pdbInput
		if fragmentCheckInput:
			line += " --target "+fragmentInput
		else:
			line += " --targets "+dirInput
			
		line += " -C "+intraInput+" -J "+interInput
		line += " --rmsd_thresh "+str(rmsdInput)

		if superposeInput:
			line += " --reverse"

		line +=" "+self.parent.generalAspects

		data = {
			"title": titleInput,
			"reference": pdbInput,
			"fragment": fragmentInput,
			"fragmentRadio": fragmentCheckInput,
			"dir": dirInput,
			"intra": intraInput,
			"inter": interInput,
			"rmsd": rmsdInput,
			"superpose": superposeInput,
		}		
		self.parent.run_dialog(line, self.superpositionPath, data, self)

	def on_finish(self, exitCode, exitStatus):
		if exitCode == 0 and exitStatus == 0:
			searchPdb = glob.glob(os.path.join(self.runPath,"*.pdb"))
			for pdb in searchPdb:
				if "input_search" in pdb:
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

	def take_screenshot(self):
		self.parent.take_screenshot(self.ui.targetBrowser)

	def take_screenshot2(self):
		self.parent.take_screenshot(self.ui.referenceBrowser)
		
	def show_list(self):
		#Show the new folder
		if os.path.exists(self.superpositionPath):
			self.ui.tree.showColumn(0)
			self.ui.tree.showColumn(3)
			self.ui.tree.setRootIndex(self.ui.model.setRootPath(self.superpositionPath))
		else:
			self.ui.tree.hideColumn(0)
			self.ui.tree.hideColumn(3)

	def load_reference(self):
		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select PDB File", "","PDB File *.pdb *.ent", options=options)
		if fileName:
			self.ui.referenceLine.setText(fileName)

	def load_fragment(self):
		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select PDB File", "","PDB File *.pdb *.ent", options=options)
		if fileName:
			self.ui.fragmentLine.setText(fileName)

	def load_fragment_dir(self):
		options = QtWidgets.QFileDialog.Options()
		dirName = QtWidgets.QFileDialog.getExistingDirectory(None,"Select fragments folder", "", options=options)
		if dirName:
			self.ui.fragmentDirLine.setText(dirName)

	def representation_change(self, which):
		if which == "cartoon":
			self.ui.colorValue.setEnabled(True)
		else:
			self.ui.colorValue.setEnabled(False)

		self.show_pdb(self.pdbs, self.reference)

	def color_change(self, which):
		self.show_pdb(self.pdbs, self.reference)

	def representation_reference_change(self, which):
		if which == "cartoon":
			self.ui.colorReferenceValue.setEnabled(True)
		else:
			self.ui.colorReferenceValue.setEnabled(False)

		self.show_pdb_target(self.target)

	def color_reference_change(self, which):
		self.show_pdb_target(self.target)

	def item_selected(self, item):
		if item.isValid():
			path = self.ui.model.filePath(item)
			namePdb = item.data()
			if ".pdb" in path:
				self.ui.textOutput.clear()
				formattedPath = os.path.dirname(os.path.relpath(path, self.superpositionPath))
				formattedPath = (formattedPath.split("/"))[0]
				with open(os.path.join(self.superpositionPath,formattedPath, self.parent.infoFile), "r") as file:
					data = json.load(file)
					self.ui.titleLine.setText(data["title"])
					self.ui.referenceLine.setText(data["reference"])
					if data["fragmentRadio"] is True:
						self.ui.fragmentRadio.setChecked(True)
					else:
						self.ui.fragmentDirRadio.setChecked(True)
					self.ui.fragmentLine.setText(data["fragment"])
					self.ui.fragmentDirLine.setText(data["dir"])
					self.ui.intraSpin.setValue(int(data["intra"]))
					self.ui.interSpin.setValue(int(data["inter"]))
					self.ui.rmsdValue.setValue(float(data["rmsd"]))
					self.ui.superposeCheck.setChecked(data["superpose"])

				selected = self.ui.tree.selectionModel().selectedIndexes()
				self.pdbs = []
				self.target = []
				self.reference = False
				for items in selected:
					if items.isValid():
						path = self.ui.model.filePath(items)
						if ".pdb" in path and path not in self.pdbs:
							self.pdbs.append(path)

				if self.pdbs:
					if os.path.exists(os.path.join(self.superpositionPath,formattedPath, self.parent.outputFile)):
						with open(os.path.join(self.superpositionPath,formattedPath, self.parent.outputFile), "r") as file:
							data = json.load(file)
							if "superposition" in data:
								for items in self.pdbs:
									name = os.path.basename(items)
									if name in data["superposition"]:
										info = data["superposition"][name]["rmsd and core"].split()
										self.ui.textOutput.append("<b>"+name+"</b> -> Rmsd: "+str(round(float(info[0]),2))+", Core: "+info[1])

					if os.path.exists(self.ui.referenceLine.text()):
						self.pdbs.append(self.ui.referenceLine.text())
						self.reference = True

					if self.ui.fragmentRadio.isChecked():
						if os.path.exists(self.ui.fragmentLine.text()):
							self.target = [self.ui.fragmentLine.text()]
					else:
						if os.path.exists(os.path.join(self.ui.fragmentDirLine.text(),namePdb)):
							self.target = [os.path.join(self.ui.fragmentDirLine.text(),namePdb)]
							
				self.show_pdb_target(self.target)
				self.show_pdb(self.pdbs, self.reference)

	def show_pdb_target(self, pdbs):
		#Load the .hmtl in /dist/ngl.html and replace the fields with the new parameters
		htmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.html"))
		with open(htmlPath , "r+") as file:
			html = file.read()

		jsPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.js"))
		jsLocalPath = QtCore.QUrl.fromLocalFile(jsPath)

		if self.ui.colorReferenceValue.currentText() == "secondary structure" or self.ui.representationReferenceValue.currentText() != "cartoon":
			rep = "\""+self.ui.representationReferenceValue.currentText()+"\",{colorScheme:\"sstruc\"}"
		elif self.ui.colorReferenceValue.currentText() == "residue":
			rep = "\""+self.ui.representationReferenceValue.currentText()+"\",{colorScheme:\"residueindex\"},{colorScale:\"Red-Blue\"}"
		else:
			rep = "\""+self.ui.representationReferenceValue.currentText()+"\",{colorScheme:\"chainid\"},{colorScale:\"Set1\"}"

		pdbRep = ""
		for pdb in pdbs:
			pdbRep += "stage.loadFile(\""+QtCore.QUrl.fromLocalFile(pdb).toString()+"\").then(function (o) { o.addRepresentation("+rep+");stage.autoView();});"

		html = html.replace("JS", jsLocalPath.toString())
		html = html.replace("ADDINPUT", pdbRep)

		self.ui.referenceBrowser.setHtml(html)

	def show_pdb(self, pdbs, ref):
		#Load the .hmtl in /dist/ngl.html and replace the fields with the new parameters
		htmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.html"))
		with open(htmlPath , "r+") as file:
			html = file.read()

		jsPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.js"))
		jsLocalPath = QtCore.QUrl.fromLocalFile(jsPath)
		pdbsAux = pdbs.copy()

		pdbRep = ""

		if self.ui.colorValue.currentText() == "secondary structure" or self.ui.representationValue.currentText() != "cartoon":
			rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"sstruc\"}"
		elif self.ui.colorValue.currentText() == "residue":
			rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"residueindex\"},{colorScale:\"Red-Blue\"}"
		else:
			rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"chainid\"},{colorScale:\"Set1\"}"

		if ref:
			reference = pdbsAux.pop()
			pdbRep = "stage.loadFile(\""+QtCore.QUrl.fromLocalFile(reference).toString()+"\").then(function (o) { o.addRepresentation("+rep+");stage.autoView();});"
		
		for pdb in pdbsAux:
			pdbRep += "stage.loadFile(\""+QtCore.QUrl.fromLocalFile(pdb).toString()+"\").then(function (o) { o.addRepresentation(\"cartoon\");stage.autoView();});"

		html = html.replace("JS", jsLocalPath.toString())
		html = html.replace("ADDINPUT", pdbRep)

		self.ui.targetBrowser.setHtml(html)

			
				