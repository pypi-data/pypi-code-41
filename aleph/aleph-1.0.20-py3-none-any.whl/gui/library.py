from PySide2 import QtWidgets, QtCore
from ui_library import Ui_Library
from download_pdb import DownloadPdb
import os, glob, json, re

colors = ["yellow","green","red","blue","brown","orange","pink","purple","lime","cyan"]

class Library(QtWidgets.QWidget):
	def __init__(self, parent):   
		super().__init__(parent)
		self.parent = parent
		self.libraryPath = ""
		self.defaultNameRun = "run"
		self.ui = Ui_Library()
		self.ui.setupUI(self, self.parent.check_connection())
		self.init_ui()
		self.pdbs = []

	def set_project_directory(self, path):
		self.libraryPath = os.path.join(path,"aleph_library")
		self.show_list()										

	def init_ui(self):
		self.ui.pdbLoad.clicked.connect(self.load_pdb)
		self.ui.seqLoad.clicked.connect(self.load_seq)
		self.ui.pdbDownload.clicked.connect(self.download_pdb)
		self.ui.templateLoad.clicked.connect(self.load_template)
		self.ui.templateCoot.clicked.connect(self.open_coot)
		self.ui.gridLoad.clicked.connect(self.load_grid)
		self.ui.excludeCheck.clicked.connect(self.exclude_clicked)
		self.ui.excludeLoad.clicked.connect(self.load_exclude)
		self.ui.runValue.currentTextChanged.connect(self.grid_changed)
		self.ui.alphaSlider.valueChanged.connect(lambda: self.value_change("alpha"))
		self.ui.betaSlider.valueChanged.connect(lambda: self.value_change("beta"))
		self.ui.minRmsdValue.valueChanged.connect(self.min_rmsd_changed)
		self.ui.maxRmsdValue.valueChanged.connect(self.max_rmsd_changed)
		self.ui.representationValue.currentTextChanged.connect(self.representation_change)
		self.ui.colorValue.currentTextChanged.connect(self.color_change)
		self.ui.representationTemplateValue.currentTextChanged.connect(self.representation_template_change)
		self.ui.colorTemplateValue.currentTextChanged.connect(self.color_template_change)
		self.ui.tree.clicked.connect(self.item_selected)
		self.ui.clusteringValue.currentTextChanged.connect(self.cluster_change)
		self.ui.saveButton.clicked.connect(self.take_screenshot)
		self.ui.saveButton2.clicked.connect(self.take_screenshot2)
		self.ui.templateCheck.stateChanged.connect(self.template_check)
		self.ui.templateValue.currentTextChanged.connect(self.template_change)

	def run_library(self):
		settings = QtCore.QSettings()
		alephPath = settings.value("aleph_path")
		titleInput = re.sub('[ /:]', '', self.ui.titleLine.text())
		pdbCheckInput = self.ui.pdbRadio.isChecked()
		pdbInput = self.ui.pdbLine.text()
		seqCheckInput = self.ui.seqRadio.isChecked()
		seqInput = self.ui.seqLine.text()
		cathCheckInput = self.ui.cathRadio.isChecked()
		cathInput = self.ui.cathLine.text()
		templateInput = self.ui.templateLine.text()
		alphaInput = str(float(self.ui.alphaSlider.value()/100))
		betaInput = str(float(self.ui.betaSlider.value()/100))
		runInput = self.ui.runValue.currentText()
		runConfigInput = self.ui.gridLine.text()
		minRmsdInput = str(self.ui.minRmsdValue.value())
		maxRmsdInput = str(self.ui.maxRmsdValue.value())
		intraInput = str(self.ui.intraSpin.value())
		interInput = str(self.ui.interSpin.value())
		clusterInput = self.ui.clusterGroupBox.isChecked()
		clusterMode = self.ui.clusteringValue.currentText()
		rmsdValueInput = str(self.ui.rmsdValue.value())
		samplingValueInput = str(self.ui.samplingValue.value())
		rangeValueInput = str(self.ui.rangeValue.value())
		rangeClusterValueInput = str(self.ui.rangeClusterValue.value())
		testInput = self.ui.testCheck.isChecked()
		excludeCheckInput = self.ui.excludeCheck.isChecked()
		excludeInput = self.ui.excludeLine.text()
		representativeCheckInput = self.ui.representativeCheck.isChecked()

		if titleInput == "":
			titleInput = re.sub('[ /:]', '', os.path.splitext(os.path.basename(templateInput))[0])

		line = alephPath+" generate_library --pdbmodel "+templateInput
		if pdbCheckInput:
			line += " --directory_database "+pdbInput
		elif seqCheckInput:
			line += " --target_sequence "+seqInput
		else:
			line += " --cath_id "+cathInput
		line += " --strictness_ah "+alphaInput+" --strictness_bs "+betaInput
		if runInput != "multiprocessing":
			line += " --"+runInput+" "+runConfigInput
		line +=" --rmsd_min "+minRmsdInput+" --rmsd_max "+maxRmsdInput
		line += " -C "+intraInput+" -J "+interInput
		if clusterInput:
			if clusterMode == "Group by rmsd":
				line += " --clustering_mode rmsd --rmsd_clustering "+rmsdValueInput
			elif clusterMode == "Random sampling":
				line += " --clustering_mode random_sampling --number_of_clusters "+samplingValueInput
			else:
				line += " --clustering_mode rmsd_range --number_of_ranges "+rangeValueInput+" --number_of_clusters "+rangeClusterValueInput
		else:
			line += " --clustering_mode no_clustering"
		if excludeCheckInput:
			line += " --exclude_sequence "+excludeInput
		if representativeCheckInput:
			line += " --representative"
		if testInput:
			line += " --test"

		line +=" "+self.parent.generalAspects
		data = {
			"title": titleInput,
			"pdbCheck": pdbCheckInput,
			"pdb": pdbInput,
			"seqCheck": seqCheckInput,
			"seq": seqInput,
			"cathCheck": cathCheckInput,
			"cath": cathInput,
			"template": templateInput,
			"alpha": alphaInput,
			"beta": betaInput,
			"run": runInput,
			"configuration": runConfigInput,
			"minRmsd": minRmsdInput,
			"maxRmsd": maxRmsdInput,
			"intra": intraInput,
			"inter": interInput,
			"cluster": clusterInput,
			"rmsd": rmsdValueInput,
			"clusterMode": clusterMode,
			"sampling": samplingValueInput,
			"range": rangeValueInput,
			"rangeCluster": rangeClusterValueInput,
			"test": testInput,
			"excludeCheck": excludeCheckInput,
			"exclude": excludeInput,
			"representativeCheck": representativeCheckInput,
		}		
		self.parent.run_dialog(line, self.libraryPath, data, self)
		
	def item_selected(self, item):
		if item.isValid():
			path = self.ui.model.filePath(item)
			if ".pdb" in path:
				self.ui.textOutput.clear()
				formattedPath = os.path.dirname(os.path.relpath(path, self.libraryPath))
				formattedPath = (formattedPath.split("/"))[0]				
				with open(os.path.join(self.libraryPath,formattedPath, self.parent.infoFile), "r") as file:
					data = json.load(file)
					if data["pdbCheck"] is True:
						self.ui.pdbRadio.setChecked(True)
					elif data["seqCheck"] is True:
						self.ui.seqRadio.setChecked(True)
					else:
						self.ui.cathRadio.setChecked(True)
					self.ui.titleLine.setText(data["title"])
					self.ui.pdbLine.setText(data["pdb"])
					self.ui.seqLine.setText(data["seq"])
					self.ui.cathLine.setText(data["cath"])
					self.ui.templateLine.setText(data["template"])
					self.ui.alphaSlider.setValue(float(data["alpha"])*100)
					self.ui.betaSlider.setValue(float(data["beta"])*100)
					self.ui.runValue.setCurrentText(data["run"])
					self.ui.gridLine.setText(data["configuration"])
					self.ui.minRmsdValue.setValue(float(data["minRmsd"]))
					self.ui.maxRmsdValue.setValue(float(data["maxRmsd"]))
					self.ui.intraSpin.setValue(int(data["intra"]))
					self.ui.interSpin.setValue(int(data["inter"]))
					self.ui.clusterGroupBox.setChecked(data["cluster"])
					self.ui.clusteringValue.setCurrentText(data["clusterMode"])
					self.ui.rmsdValue.setValue(float(data["rmsd"]))
					self.ui.samplingValue.setValue(int(data["sampling"]))
					self.ui.rangeValue.setValue(int(data["range"]))
					self.ui.rangeClusterValue.setValue(int(data["rangeCluster"]))
					self.ui.testCheck.setChecked(data["test"])
					self.ui.excludeCheck.setChecked(data["excludeCheck"])
					self.ui.excludeLine.setText(data["exclude"])
					self.ui.representativeCheck.setChecked(data["representativeCheck"])
					if os.path.exists(self.ui.templateLine.text()):
						self.show_pdb([self.ui.templateLine.text()], True)

				#when we select an item in the qtreeview
				selected = self.ui.tree.selectionModel().selectedIndexes()
				self.pdbs = []
				for items in selected:
					if items.isValid():
						path = self.ui.model.filePath(items)
						if ".pdb" in path and path not in self.pdbs:
							self.pdbs.append(os.path.join(path))

				if self.pdbs:
					if os.path.exists(os.path.join(self.libraryPath,formattedPath, self.parent.outputFile)):
						with open(os.path.join(self.libraryPath,formattedPath, self.parent.outputFile), "r") as file:
							data = json.load(file)
							#if "library_generation" in data and "superposition" in data["library_generation"]:
							if "library generation" in data and "superposition" in data["library generation"]:
								for items in self.pdbs:
									name = os.path.basename(items)
									if name in data["library generation"]["superposition"]:
										info = data["library generation"]["superposition"][name]["rmsd and core"].split()
										self.ui.textOutput.append("<b>"+name+"</b> -> Rmsd: "+str(round(float(info[0]),2))+", Core: "+info[1])					

				self.show_pdb(self.pdbs)

	def on_finish(self, exitCode, exitStatus):
		if exitCode == 0 and exitStatus == 0:
			searchPdb = glob.glob(os.path.join(self.runPath,"*.pdb"))
			for pdb in searchPdb:
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

	def template_check(self, state):
		self.show_pdb(self.pdbs)

	def template_change(self):
		if self.ui.templateCheck.isChecked():
			self.show_pdb(self.pdbs)

	def load_pdb(self):
		options = QtWidgets.QFileDialog.Options()
		dirName = QtWidgets.QFileDialog.getExistingDirectory(None,"Select PDB folder", "", options=options)
		if dirName:
			self.ui.pdbLine.setText(dirName)

	def load_seq(self):
		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select Seq File", "","Seq File (*.seq, *.fasta)", options=options)
		if fileName:
			self.ui.seqLine.setText(fileName)

	def download_pdb(self):
		wizard = DownloadPdb()
		wizard.exec_()
		dirName = wizard.get_directory()
		if dirName != "":
			self.ui.pdbLine.setText(dirName)

	def load_template(self):
		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select PDB File", "","PDB File *.pdb *.ent", options=options)
		if fileName:
			self.ui.templateLine.setText(fileName)
			self.show_pdb([fileName], True)

	def load_grid(self):
		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select configuration File", "","", options=options)
		if fileName:
			self.ui.gridLine.setText(fileName)

	def load_exclude(self):
		options = QtWidgets.QFileDialog.Options()
		fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select a FASTA File", "","FASTA File *.fasta", options=options)
		if fileName:
			self.ui.excludeLine.setText(fileName)

	def open_coot(self):
		settings = QtCore.QSettings()
		cootPath = settings.value("coot_path")
		line = cootPath+" "+self.ui.templateLine.text()
		print(line)
		process = QtCore.QProcess(self)
		process.finished.connect(self.on_finish_coot)
		process.start(line)

	def on_finish_coot(self):
		self.show_pdb([self.ui.templateLine.text()], True)

	def take_screenshot(self):
		self.parent.take_screenshot(self.ui.browser)

	def take_screenshot2(self):
		self.parent.take_screenshot(self.ui.templateBrowser)

	def representation_change(self, which):
		if which == "cartoon":
			self.ui.colorValue.setEnabled(True)
		else:
			self.ui.colorValue.setEnabled(False)

		self.show_pdb(self.pdbs)

	def exclude_clicked(self, clicked):
		if clicked:
			self.ui.excludeLine.setEnabled(True)
			self.ui.excludeLoad.setEnabled(True)
		else:
			self.ui.excludeLine.setEnabled(False)
			self.ui.excludeLoad.setEnabled(False)

	def color_change(self, which):
		self.show_pdb(self.pdbs)

	def representation_template_change(self, which):
		if which == "cartoon":
			self.ui.colorTemplateValue.setEnabled(True)
		else:
			self.ui.colorTemplateValue.setEnabled(False)

		self.show_pdb([self.ui.templateLine.text()], True)

	def color_template_change(self, which):
		self.show_pdb([self.ui.templateLine.text()], True)
		
	def value_change(self, which):
		if which == "alpha":
			value = float(self.ui.alphaSlider.value()/100)
			self.ui.alphaValue.setText("{:.2f}".format(value).replace(".",","))
		else:
			value = float(self.ui.betaSlider.value()/100)
			self.ui.betaValue.setText("{:.2f}".format(value).replace(".",","))

	def min_rmsd_changed(self, value):
		if value > self.ui.maxRmsdValue.value():
			self.ui.minRmsdValue.setValue(self.ui.maxRmsdValue.value())

	def max_rmsd_changed(self, value):
		if value < self.ui.minRmsdValue.value():
			self.ui.maxRmsdValue.setValue(self.ui.minRmsdValue.value())

	def grid_changed(self, which):
		if which != "multiprocessing":
			self.ui.gridLabel.setEnabled(True)
			self.ui.gridLine.setEnabled(True)
			self.ui.gridLoad.setEnabled(True)
		else:
			self.ui.gridLabel.setEnabled(False)
			self.ui.gridLine.setEnabled(False)
			self.ui.gridLoad.setEnabled(False)

	def cluster_change(self, which):
		if which == "Group by rmsd":
			self.ui.rmsdModeWidget.show()
			self.ui.samplingModeWidget.hide()
			self.ui.rangeModeWidget.hide()
		elif which == "Random sampling":
			self.ui.rmsdModeWidget.hide()
			self.ui.samplingModeWidget.show()
			self.ui.rangeModeWidget.hide()
		else:
			self.ui.rmsdModeWidget.hide()
			self.ui.samplingModeWidget.hide()
			self.ui.rangeModeWidget.show()

	def show_list(self):
		#Show the new folder
		if os.path.exists(self.libraryPath):
			self.ui.tree.showColumn(0)
			self.ui.tree.showColumn(3)
			self.ui.tree.setRootIndex(self.ui.model.setRootPath(self.libraryPath))
		else:
			self.ui.tree.hideColumn(0)
			self.ui.tree.hideColumn(3)

	def show_pdb(self, pdbs, template=False):
		#Load the .hmtl in /dist/ngl.html and replace the fields with the new parameters
		htmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.html"))
		with open(htmlPath , "r+") as file:
			html = file.read()

		settings = QtCore.QSettings()
		templateColor = settings.value("color")

		jsPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist/ngl.js"))
		jsLocalPath = QtCore.QUrl.fromLocalFile(jsPath)

		pdbRep = ""

		if self.ui.templateCheck.isChecked() and os.path.exists(self.ui.templateLine.text()) and not template:
			fileLocalPath = QtCore.QUrl.fromLocalFile(self.ui.templateLine.text())
			pdbRep = "stage.loadFile(\""+fileLocalPath.toString()+"\").then(function (o) {\
        					o.addRepresentation(\""+self.ui.templateValue.currentText()+"\", {color:\""+templateColor+"\"});});"

		if not template:
			if self.ui.colorValue.currentText() == "secondary structure" or self.ui.representationValue.currentText() != "cartoon":
				rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"sstruc\"}"
			elif self.ui.colorValue.currentText() == "residue":
				rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"residueindex\"},{colorScale:\"Red-Blue\"}"
			elif self.ui.colorValue.currentText() == "chain id":
				rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"chainid\"},{colorScale:\"Set1\"}"

		else:
			if self.ui.colorTemplateValue.currentText() == "secondary structure" or self.ui.representationTemplateValue.currentText() != "cartoon":
				rep = "\""+self.ui.representationTemplateValue.currentText()+"\",{colorScheme:\"sstruc\"}"
			elif self.ui.colorTemplateValue.currentText() == "residue":
				rep = "\""+self.ui.representationTemplateValue.currentText()+"\",{colorScheme:\"residueindex\"},{colorScale:\"Red-Blue\"}"
			else:
				rep = "\""+self.ui.representationTemplateValue.currentText()+"\",{colorScheme:\"chainid\"},{colorScale:\"Set1\"}"

		if self.ui.colorValue.currentText() == "model" and not template:
			for idx,pdb in enumerate(pdbs):
				pdbRep += "stage.loadFile(\""+QtCore.QUrl.fromLocalFile(pdb).toString()+"\").then(function (o) { o.addRepresentation(\""+self.ui.representationValue.currentText()+"\",{color:\""+colors[idx%10]+"\"});stage.autoView();});"
		else:
			for pdb in pdbs:
				pdbRep += "stage.loadFile(\""+QtCore.QUrl.fromLocalFile(pdb).toString()+"\").then(function (o) { o.addRepresentation("+rep+");stage.autoView();});"

		html = html.replace("JS", jsLocalPath.toString())
		html = html.replace("ADDINPUT", pdbRep)

		if not template:
			self.ui.browser.setHtml(html)
		else:
			self.ui.templateBrowser.setHtml(html)