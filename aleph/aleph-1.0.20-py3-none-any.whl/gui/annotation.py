from PySide2 import QtWidgets, QtCore
from ui_annotation import Ui_Annotation
import os, glob, json, re

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np

class Annotation(QtWidgets.QWidget):
	def __init__(self, parent):   
		super().__init__(parent)
		self.parent = parent
		self.annotationPath = ""
		self.oldIndex = ""
		self.formattedPath = ""
		self.ui = Ui_Annotation()
		self.ui.setupUI(self)
		self.init_ui()

	def set_project_directory(self, path):
		self.annotationPath = os.path.join(path,"aleph_annotation")
		self.show_list()

	def init_ui(self):
		self.ui.pdbLoad.clicked.connect(self.load_pdb)
		self.ui.saveButton.clicked.connect(self.take_screenshot)
		self.ui.alphaSlider.valueChanged.connect(lambda: self.value_change("alpha"))
		self.ui.betaSlider.valueChanged.connect(lambda: self.value_change("beta"))
		self.ui.tree.clicked.connect(self.item_selected)
		self.ui.representationValue.currentTextChanged.connect(self.representation_change)
		self.ui.colorValue.currentTextChanged.connect(self.color_change)
		self.ui.templateCheck.stateChanged.connect(self.template_check)
		self.ui.templateAdvancedCheck.stateChanged.connect(self.tab_advanced_changed)
		self.ui.vectorsCheck.stateChanged.connect(self.vectors_check)
		self.ui.templateValue.currentTextChanged.connect(self.template_change)
		self.ui.tabs.currentChanged.connect(self.tab_changed)
		self.ui.advancedTabs.currentChanged.connect(self.tab_advanced_changed)

	def run_annotation(self):
		settings = QtCore.QSettings()
		alephPath = settings.value("aleph_path")
		titleInput = re.sub('[ /:]', '', self.ui.titleLine.text())
		pdbInput = self.ui.pdbLine.text()
		alphaInput = str(float(self.ui.alphaSlider.value()/100))
		betaInput = str(float(self.ui.betaSlider.value()/100))
		if titleInput == "":
			titleInput = re.sub('[ /:]', '', os.path.splitext(os.path.basename(pdbInput))[0])

		data = { "title": titleInput,  "pdb": pdbInput, "alpha": alphaInput, "beta": betaInput }
		line = alephPath+" annotate --pdbmodel "+pdbInput+" --strictness_ah "+alphaInput+" --strictness_bs "+betaInput+" "+self.parent.generalAspects
		self.parent.run_dialog(line, self.annotationPath, data, self)

	def item_selected(self, item):
		#when we select an item in the qtreeview
		if item.isValid():
			path = self.ui.model.filePath(item)
			self.formattedPath = os.path.join(self.annotationPath, os.path.dirname(os.path.relpath(path, self.annotationPath)))
			if ".pdb" in path:
				with open(os.path.join(self.formattedPath, self.parent.infoFile), "r") as file:
					data = json.load(file)
					self.ui.titleLine.setText(data["title"])
					self.ui.pdbLine.setText(data["pdb"])
					self.ui.alphaSlider.setValue(float(data["alpha"])*100)
					self.ui.betaSlider.setValue(float(data["beta"])*100)
				self.show_pdb(path)
	def take_screenshot(self):
		self.parent.take_screenshot(self.ui.browser)
		
	def template_check(self, state):
		self.item_selected(self.ui.tree.currentIndex())

	def vectors_check(self, state):
		self.item_selected(self.ui.tree.currentIndex())

	def template_change(self):
		if self.ui.templateCheck.isChecked():
			self.item_selected(self.ui.tree.currentIndex())

	def representation_change(self, which):
		if which == "cartoon":
			self.ui.colorValue.setEnabled(True)
		else:
			self.ui.colorValue.setEnabled(False)

		self.item_selected(self.ui.tree.currentIndex())

	def color_change(self, which):
		self.item_selected(self.ui.tree.currentIndex())

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

	def show_list(self):
		#Show the new folder
		if os.path.exists(self.annotationPath):
			self.ui.tree.showColumn(0)
			self.ui.tree.showColumn(3)
			self.ui.tree.setRootIndex(self.ui.model.setRootPath(self.annotationPath))
		else:
			self.ui.tree.hideColumn(0)
			self.ui.tree.hideColumn(3)

	def tab_changed(self, index):
		if index == 1:
			if self.ui.tree.currentIndex().isValid() and self.oldIndex != self.ui.tree.currentIndex():
				self.tab_advanced_changed(index)
			self.oldIndex = self.ui.tree.currentIndex()

	def tab_advanced_changed(self, index):
		if self.ui.tree.currentIndex().isValid():
			settings = QtCore.QSettings()
			size = settings.value("font_size")
			if self.ui.advancedTabs.currentIndex() == 0:
				self.create_cvl_graph(self.formattedPath, size)
			elif self.ui.advancedTabs.currentIndex() == 1:
				self.create_angles_graph(self.formattedPath, size)
			elif self.ui.advancedTabs.currentIndex() == 2:
				self.create_ca_graph(self.formattedPath, size)
			elif self.ui.advancedTabs.currentIndex() == 3:
				self.create_angles2_graph(self.formattedPath, size)

	def create_cvl_graph(self, path, size):
		self.ui.cvlFigure.clf()
		if os.path.exists(os.path.join(path, self.parent.outputFile)):
			with open(os.path.join(path, self.parent.outputFile), "r") as file:
				data = json.load(file)
				if "plots" in data and "CVL_pic" in data["plots"]:
					x = data["plots"]["CVL_pic"]["cvids"]
					y = data["plots"]["CVL_pic"]["cvls"]
					z = data["plots"]["CVL_pic"]["sstype"]
					q = data["plots"]["CVL_pic"]["label"]
					cmap = {"ah": "r", "bs": "y", "coil": "b"}
					plt.figure(self.ui.cvlFigure.number)
					ax = plt.subplot()

					if not self.ui.templateAdvancedCheck.isChecked():
						xyzq = list(zip(x, y, z, q))
						new = [i for i in xyzq if i[2] != "coil"]
						x,y,z,q = map(list, zip(*new))

					ax.scatter(x, y, s=25, color=[cmap[u] for u in z], label=[cmap[u] for u in z])
					ax.plot(x, y, color='green', linewidth=2)
					for xyq in zip(x, y, q):
						ax.annotate(xyq[2].replace("_",""), xy=xyq[:2], textcoords="data", ha='center', va="bottom", size=size)
					ax.axhline(y=2.2, color='b')
					trans = transforms.blended_transform_factory(ax.transAxes, ax.transData)
					ax.annotate("alpha", xy =(1.01,2.2), xycoords=trans, clip_on=False, va='center', fontsize=size)
					ax.axhline(y=1.4, color='b')
					ax.annotate("beta", xy =(1.01,1.4), xycoords=trans, clip_on=False, va='center', fontsize=size)
					plt.title("CVL graph", fontsize=(int(size)+5))
					plt.ylabel("CVL", fontsize=int(size)+2)
					plt.xlabel("CV id", fontsize=int(size)+2)
					plt.xticks(np.arange(np.min(x), np.max(x), 1.0), fontsize=size)
					plt.yticks(fontsize=size)
					legend_elements = [Line2D([0], [0], marker='o', color='w', label='Alpha',markerfacecolor='r', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Beta',markerfacecolor='y', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Coil',markerfacecolor='b', markersize=10)]
					plt.legend(handles=legend_elements, loc='upper right', fontsize=size)
		self.ui.cvlCanvas.draw()

	def create_angles_graph(self, path, size):
		self.ui.anglesFigure.clf()
		if os.path.exists(os.path.join(path, self.parent.outputFile)):
			with open(os.path.join(path, self.parent.outputFile), "r") as file:
				data = json.load(file)
				if "plots" in data and "Angles_pic" in data["plots"]:
					x = data["plots"]["Angles_pic"]["cvids"]
					y = data["plots"]["Angles_pic"]["cv_anles"]
					z = data["plots"]["Angles_pic"]["sstype"]
					q = data["plots"]["Angles_pic"]["label"]
					k = data["plots"]["Angles_pic"]["ca_distance"]
					o = data["plots"]["Angles_pic"]["fragment_start"]
					n = data["plots"]["Angles_pic"]["fragment_mean"]
					l = data["plots"]["Angles_pic"]["fragment_label"]
					cmap = {"ah": "r", "bs": "y", "coil": "b"}
					plt.figure(self.ui.anglesFigure.number)

					if not self.ui.templateAdvancedCheck.isChecked():
						xyzq = list(zip(x, y, z, q))
						new = [i for i in xyzq if i[2] != "coil"]
						x,y,z,q = map(list, zip(*new))
						o = []
						n = []
						l = []

					plt.scatter(x, y, s=25, color=[cmap[u] for u in z])
					plt.plot(x, y, linewidth=2, color="green")
					plt.scatter(o, n, s=25, linewidth=2, color="g")
					for xyq in zip(x, y, q, z):
					    plt.annotate(xyq[2].replace("_",""), xy=xyq[:2], textcoords='data', ha='center', va="bottom", size=size)
					for onl in zip(o, n, l):
					    plt.annotate(onl[2].replace("_",""), xy=onl[:2], textcoords='data', ha='center', va="bottom", size=size)
					plt.title("Angles graph", fontsize=(int(size)+5))
					plt.ylabel("Angle", fontsize=int(size)+2)
					plt.xlabel("CV id", fontsize=int(size)+2)
					plt.xticks(np.arange(np.min(x), np.max(x), 1.0), fontsize=size)
					plt.yticks(fontsize=size)
					legend_elements = [Line2D([0], [0], marker='o', color='w', label='Alpha',markerfacecolor='r', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Beta',markerfacecolor='y', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Coil',markerfacecolor='b', markersize=10)]
					plt.legend(handles=legend_elements, loc='upper right', fontsize=size)
		self.ui.anglesCanvas.draw()

	def create_ca_graph(self, path, size):
		self.ui.caFigure.clf()
		if os.path.exists(os.path.join(path, self.parent.outputFile)):
			with open(os.path.join(path, self.parent.outputFile), "r") as file:
				data = json.load(file)
				if "plots" in data and "Angles_pic" in data["plots"]:
					x = data["plots"]["Angles_pic"]["cvids"]
					y = data["plots"]["Angles_pic"]["cv_anles"]
					z = data["plots"]["Angles_pic"]["sstype"]
					q = data["plots"]["Angles_pic"]["label"]
					k = data["plots"]["Angles_pic"]["ca_distance"]
					cmap = {"ah": "r", "bs": "y", "coil": "b"}
					plt.figure(self.ui.caFigure.number)

					if not self.ui.templateAdvancedCheck.isChecked():
						xyzqk = list(zip(x, y, z, q, k))
						new = [i for i in xyzqk if i[2] != "coil"]
						x,y,z,q,k = map(list, zip(*new))

					plt.scatter(x, k, s=25, color=[cmap[u] for u in z])
					plt.plot(x, k, linewidth=2, color="green")
					for xk in zip(x, k, q):
						plt.annotate(xk[2].replace("_",""), xy=xk[:2], textcoords='data', ha='center', va="bottom", size=size)
					plt.title("Ca-Ca distances", fontsize=(int(size)+5))
					plt.ylabel("Angstrom", fontsize=size)
					plt.xlabel("CV id", fontsize=size)
					plt.xticks(np.arange(np.min(x), np.max(x), 1.0), fontsize=size)
					plt.yticks(fontsize=size)
					plt.ylim((0, 4))
					legend_elements = [Line2D([0], [0], marker='o', color='w', label='Alpha',markerfacecolor='r', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Beta',markerfacecolor='y', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Coil',markerfacecolor='b', markersize=10)]
					plt.legend(handles=legend_elements, loc='upper right', fontsize=size)
		self.ui.caCanvas.draw()

	def create_angles2_graph(self, path, size):
		self.ui.angles2Figure.clf()
		if os.path.exists(os.path.join(path, self.parent.outputFile)):
			with open(os.path.join(path, self.parent.outputFile), "r") as file:
				data = json.load(file)
				if "plots" in data and "Angles_pic" in data["plots"]:
					x = data["plots"]["Angles_pic"]["cvids"]
					y = data["plots"]["Angles_pic"]["cv_anles"]
					z = data["plots"]["Angles_pic"]["sstype"]
					cmap = {"ah": "r", "bs": "y", "coil": "b"}
					plt.figure(self.ui.angles2Figure.number)

					if not self.ui.templateAdvancedCheck.isChecked():
						xyz = list(zip(x, y, z))
						new = [i for i in xyz if i[2] != "coil"]
						x,y,z = map(list, zip(*new))

					#v, ax = plt.subplots(1, sharex=True, subplot_kw=dict(polar=True))
					ax = plt.subplot(111, projection='polar')
					ax.scatter([(np.pi / 180.0) * sole for sole in y], x, color=[cmap[u] for u in z])
					ax.grid(True)
					ax.set_rmax(np.max(x))
					ax.tick_params(labelsize=size)
					legend_elements = [Line2D([0], [0], marker='o', color='w', label='Alpha',markerfacecolor='r', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Beta',markerfacecolor='y', markersize=10),
									Line2D([0], [0], marker='o', color='w', label='Coil',markerfacecolor='b', markersize=10)]
					plt.legend(handles=legend_elements, loc='upper right', fontsize=size)
		self.ui.angles2Canvas.draw()

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
			pdbRep += "stage.loadFile(\""+fileLocalPath.toString()+"\").then(function (o) {\
        					o.addRepresentation(\""+self.ui.templateValue.currentText()+"\", {color:\""+templateColor+"\"});});"

		if self.ui.colorValue.currentText() == "secondary structure" or self.ui.representationValue.currentText() != "cartoon":
			rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"sstruc\"}"
		elif self.ui.colorValue.currentText() == "residue":
			rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"residueindex\"},{colorScale:\"Red-Blue\"}"
		elif self.ui.colorValue.currentText() == "chain id":
			rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"chainid\"},{colorScale:\"Set1\"}"
		else:
			pdbAux = pdbPath.replace(os.path.basename(pdbPath), "strictnesses.pdb")
			if os.path.exists(pdbAux):
				pdbLocalPath = QtCore.QUrl.fromLocalFile(pdbAux)
			rep = "\""+self.ui.representationValue.currentText()+"\",{colorScheme:\"bfactor\", colorScale:[\'red\',\'blue\']}"
		pdbRep += "stage.loadFile(\""+pdbLocalPath.toString()+"\").then(function (o) { o.addRepresentation("+rep+");stage.autoView();});"

		if self.ui.vectorsCheck.isChecked():
			if os.path.exists(os.path.join(self.formattedPath, self.parent.outputFile)):
				with open(os.path.join(self.formattedPath, self.parent.outputFile), "r") as file:
					data = json.load(file)
					if "cvs" in data:
						pdbRep += "var shape = new NGL.Shape( \"shape\" );"
						for i in range(len(data["cvs"])):
							value = data["cvs"][str(i)]
							pdbRep += "shape.addArrow( "+str(value["start"])+", "+str(value["end"])+", [ 0, 0.7, 0 ], 0.2 );"
						pdbRep += "var shapeComp = stage.addComponentFromObject( shape );"
						pdbRep += "shapeComp.addRepresentation( \"buffer\" );"

		html = html = html.replace("JS", jsLocalPath.toString())
		html = html.replace("ADDINPUT", pdbRep)
		self.ui.browser.setHtml(html)


