from PySide2 import QtWidgets, QtCore, QtWebEngineWidgets, QtGui
from OpenGL import GL

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt

import os

class Ui_Annotation:
	def setupUI(self, Annotation):
		self.gridLayout = QtWidgets.QGridLayout(Annotation)
		self.gridLayout.setObjectName("gridLayout")

		self.splitter = QtWidgets.QSplitter(Annotation)
		self.splitter.setObjectName("splitter")
		self.splitter.setOrientation(QtCore.Qt.Vertical)
		self.splitter.setHandleWidth(15)
		#self.splitter.setStyleSheet("QSplitter::handle{image:url("+os.path.join(os.path.dirname(__file__),"img/splitter.png")+");}");

		self.topGroupBox = QtWidgets.QGroupBox(self.splitter)
		self.topGroupBox.setObjectName("topGroupBox")
		self.topGroupBox.setTitle("Graph annotation")

		self.topLayout = QtWidgets.QGridLayout(self.topGroupBox)

		self.topLayout.setObjectName("topLayout")

		self.titleLabel = QtWidgets.QLabel(self.topGroupBox)
		self.titleLabel.setObjectName("titleLabel")
		self.titleLabel.setText("Job title")
		self.topLayout.addWidget(self.titleLabel, 0, 0, 1, 1)
		self.titleLine = QtWidgets.QLineEdit(self.topGroupBox)
		self.titleLine.setObjectName("titleLine")
		self.titleLine.setFixedWidth(150)
		self.titleLine.setToolTip("Insert title job")
		self.topLayout.addWidget(self.titleLine, 0, 1, 1, 1)

		self.pdbLabel = QtWidgets.QLabel(self.topGroupBox)
		self.pdbLabel.setObjectName("pdbLabel")
		self.pdbLabel.setText("Pdb")
		self.topLayout.addWidget(self.pdbLabel, 1, 0, 1, 1)
		self.pdbLine = QtWidgets.QLineEdit(self.topGroupBox)
		self.pdbLine.setObjectName("pdbLine")
		self.topLayout.addWidget(self.pdbLine, 1, 1, 1, 1)
		self.pdbLoad = QtWidgets.QPushButton(self.topGroupBox)
		self.pdbLoad.setObjectName("pdbLoad")
		self.pdbLoad.setText("Browse")
		self.topLayout.addWidget(self.pdbLoad, 1, 2, 1, 1)

		self.line = QtWidgets.QFrame(self.topGroupBox)
		self.line.setFrameShape(QtWidgets.QFrame.VLine)
		self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.line.setObjectName("line")
		self.topLayout.addWidget(self.line, 0, 3, 2, 1)

		self.alphaLabel = QtWidgets.QLabel(self.topGroupBox)
		self.alphaLabel.setObjectName("alphaLabel")
		self.alphaLabel.setText("strictness alpha")
		self.topLayout.addWidget(self.alphaLabel, 0, 4, 1, 1)
		self.alphaSlider = QtWidgets.QSlider(self.topGroupBox)
		self.alphaSlider.setObjectName("alphaSlider")
		self.alphaSlider.setOrientation(QtCore.Qt.Horizontal)
		self.alphaSlider.setMinimum(0)
		self.alphaSlider.setMaximum(100)
		self.alphaSlider.setSingleStep(10)
		self.alphaSlider.setValue(50)
		self.topLayout.addWidget(self.alphaSlider, 0, 5, 1, 1)
		self.alphaValue = QtWidgets.QLabel(self.topGroupBox)
		self.alphaValue.setObjectName("valueAlpha")
		self.alphaValue.setText("0,50")
		self.topLayout.addWidget(self.alphaValue, 0, 6, 1, 1)

		self.betaLabel = QtWidgets.QLabel(self.topGroupBox)
		self.betaLabel.setObjectName("betaLabel")
		self.betaLabel.setText("strictness beta")
		self.topLayout.addWidget(self.betaLabel, 1, 4, 1, 1)
		self.betaSlider = QtWidgets.QSlider(self.topGroupBox)
		self.betaSlider.setObjectName("betaSlider")
		self.betaSlider.setOrientation(QtCore.Qt.Horizontal)
		self.betaSlider.setMinimum(0)
		self.betaSlider.setMaximum(100)
		self.betaSlider.setSingleStep(10)
		self.betaSlider.setValue(30)
		self.topLayout.addWidget(self.betaSlider, 1, 5, 1, 1)
		self.betaValue = QtWidgets.QLabel(self.topGroupBox)
		self.betaValue.setObjectName("betaValue")
		self.betaValue.setText("0,30")
		self.topLayout.addWidget(self.betaValue, 1, 6, 1, 1)

		self.tabs = QtWidgets.QTabWidget(self.splitter)
		self.tabs.setObjectName("tabs")

		self.middleSplitter = QtWidgets.QSplitter(self.tabs)
		self.middleSplitter.setObjectName("middleSplitter")
		self.middleSplitter.setOrientation(QtCore.Qt.Horizontal)
		self.middleSplitter.setHandleWidth(10)
		#self.middleSplitter.setStyleSheet("QSplitter::handle{image:url("+os.path.join(os.path.dirname(__file__),"img/splitter_h.png")+");}");
		policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.middleSplitter.setSizePolicy(policy)

		self.tabs.addTab(self.middleSplitter, "General")

		self.tree = QtWidgets.QTreeView(self.middleSplitter)
		policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
		self.tree.setSizePolicy(policy)
		self.model = QtWidgets.QFileSystemModel(self.tree)
		self.tree.setModel(self.model)
		self.model.setNameFilters(["*search.pdb"])
		self.model.setNameFilterDisables(False)
		self.tree.hideColumn(1)
		self.tree.hideColumn(2)
		self.tree.header().hide()
		self.tree.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.tree.sortByColumn(3, QtCore.Qt.AscendingOrder)
		self.tree.setSortingEnabled(True)

		self.structureLayoutWidget = QtWidgets.QWidget(self.middleSplitter)
		self.structureLayoutWidget.setObjectName("structureLayoutWidget")

		policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.structureLayoutWidget.setSizePolicy(policy)

		self.structureLayout = QtWidgets.QGridLayout(self.structureLayoutWidget)
		self.structureLayout.setObjectName("structureLayout")
		self.structureLayout.setContentsMargins(0, 0, 0, 0)

		self.browserLabel = QtWidgets.QLabel(self.structureLayoutWidget)
		self.browserLabel.setObjectName("browserLabel")
		self.browserLabel.setText("Annotated model")
		self.structureLayout.addWidget(self.browserLabel, 0, 0, 1, 10)

		self.browser = QtWebEngineWidgets.QWebEngineView(self.structureLayoutWidget)
		self.browser.setObjectName("browser")
		self.browser.page().setBackgroundColor(QtCore.Qt.black)
		self.browser.setSizePolicy(policy)

		self.structureLayout.addWidget(self.browser, 1, 0, 1, 12)

		spacerItem = QtWidgets.QSpacerItem(40 ,20 ,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.structureLayout.addItem(spacerItem, 2, 0, 1, 1)

		self.representationLabel = QtWidgets.QLabel(self.structureLayoutWidget)
		self.representationLabel.setObjectName("representationLabel")
		self.representationLabel.setText("Representation")
		self.structureLayout.addWidget(self.representationLabel, 2, 1, 1, 1)
		self.representationValue = QtWidgets.QComboBox(self.structureLayoutWidget)
		self.representationValue.setObjectName("representationValue")
		self.representationValue.addItems(["cartoon" , "backbone", "licorice"])
		self.structureLayout.addWidget(self.representationValue, 2, 2, 1, 1)		
		self.colorLabel = QtWidgets.QLabel(self.structureLayoutWidget)
		self.colorLabel.setObjectName("colorLabel")
		self.colorLabel.setText("color")
		self.structureLayout.addWidget(self.colorLabel, 2, 3, 1, 1)
		self.colorValue = QtWidgets.QComboBox(self.structureLayoutWidget)
		self.colorValue.setObjectName("colorValue")
		self.colorValue.addItems(["secondary structure" , "residue", "chain id", "strictness confidence"])
		self.structureLayout.addWidget(self.colorValue, 2, 4, 1, 1)	

		self.line2 = QtWidgets.QFrame(self.structureLayoutWidget)
		self.line2.setFrameShape(QtWidgets.QFrame.VLine)
		self.line2.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.line2.setObjectName("line2")
		self.structureLayout.addWidget(self.line2, 2, 5, 1, 1)

		self.templateCheck = QtWidgets.QCheckBox(self.structureLayoutWidget)
		self.templateCheck.setObjectName("templateCheck")
		self.templateCheck.setText("Show template")
		self.structureLayout.addWidget(self.templateCheck, 2, 6, 1, 1)
		self.templateValue = QtWidgets.QComboBox(self.structureLayoutWidget)
		self.templateValue.setObjectName("templateValue")
		self.templateValue.addItems(["trace" , "line"])
		self.structureLayout.addWidget(self.templateValue, 2, 7, 1, 1)

		self.line3 = QtWidgets.QFrame(self.structureLayoutWidget)
		self.line3.setFrameShape(QtWidgets.QFrame.VLine)
		self.line3.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.line3.setObjectName("line3")
		self.structureLayout.addWidget(self.line3, 2, 8, 1, 1)

		self.vectorsCheck = QtWidgets.QCheckBox(self.structureLayoutWidget)
		self.vectorsCheck.setObjectName("vectorsCheck")
		self.vectorsCheck.setText("Show characteristic vectors")
		self.structureLayout.addWidget(self.vectorsCheck, 2, 9, 1, 1)

		self.line4 = QtWidgets.QFrame(self.structureLayoutWidget)
		self.line4.setFrameShape(QtWidgets.QFrame.VLine)
		self.line4.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.line4.setObjectName("line4")
		self.structureLayout.addWidget(self.line4, 2, 10, 1, 1)

		self.saveButton = QtWidgets.QPushButton(self.structureLayoutWidget)
		self.saveButton.setObjectName("saveButton")
		self.saveButton.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"img/screenshot.png")))
		self.structureLayout.addWidget(self.saveButton, 2, 11, 1, 1)

		self.advancedTabs = QtWidgets.QTabWidget(self.tabs)
		self.advancedTabs.setObjectName("advancedTabs")
		policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.advancedTabs.setSizePolicy(policy)

		self.advancedLayout = QtWidgets.QGridLayout(self.advancedTabs)
		self.advancedLayout.setObjectName("advancedLayout")
		self.advancedLayout.setContentsMargins(0, 0, 0, 0)

		self.templateAdvancedCheck = QtWidgets.QCheckBox(self.advancedTabs)
		self.templateAdvancedCheck.setObjectName("templateAdvancedCheck")
		self.templateAdvancedCheck.setText("Show template")
		self.advancedLayout.addWidget(self.templateAdvancedCheck, 0, 2, 1, 1)
		spacerItem = QtWidgets.QSpacerItem(40 ,20 ,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.advancedLayout.addItem(spacerItem, 1, 0, 1, 1)
		spacerItem2 = QtWidgets.QSpacerItem(40 ,20 ,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.advancedLayout.addItem(spacerItem2, 1, 1, 1, 1)

		self.tabs.addTab(self.advancedTabs, "Advanced")

		self.cvlWidget = QtWidgets.QWidget(self.advancedTabs)
		self.cvlWidget.setObjectName("cvlWidget")

		self.cvlLayout = QtWidgets.QGridLayout(self.cvlWidget)
		self.cvlLayout.setObjectName("cvlLayout")
		self.cvlLayout.setContentsMargins(0, 0, 0, 0)

		self.cvlFigure = plt.figure()
		self.cvlCanvas = FigureCanvas(self.cvlFigure)
		self.cvlToolbar = NavigationToolbar(self.cvlCanvas, self.cvlWidget)
		self.cvlLayout.addWidget(self.cvlToolbar)
		self.cvlLayout.addWidget(self.cvlCanvas)

		self.advancedTabs.addTab(self.cvlWidget, "CVL")

		self.anglesWidget = QtWidgets.QWidget(self.advancedTabs)
		self.anglesWidget.setObjectName("anglesWidget")

		self.anglesLayout = QtWidgets.QGridLayout(self.anglesWidget)
		self.anglesLayout.setObjectName("anglesLayout")
		self.anglesLayout.setContentsMargins(0, 0, 0, 0)

		self.anglesFigure = plt.figure()
		self.anglesCanvas = FigureCanvas(self.anglesFigure)
		self.anglesToolbar = NavigationToolbar(self.anglesCanvas, self.anglesWidget)
		self.anglesLayout.addWidget(self.anglesToolbar)
		self.anglesLayout.addWidget(self.anglesCanvas)

		self.advancedTabs.addTab(self.anglesWidget, "Angles")

		self.caWidget = QtWidgets.QWidget(self.advancedTabs)
		self.caWidget.setObjectName("caWidget")

		self.caLayout = QtWidgets.QGridLayout(self.caWidget)
		self.caLayout.setObjectName("caLayout")
		self.caLayout.setContentsMargins(0, 0, 0, 0)

		self.caFigure = plt.figure()
		self.caCanvas = FigureCanvas(self.caFigure)
		self.caToolbar = NavigationToolbar(self.caCanvas, self.caWidget)
		self.caLayout.addWidget(self.caToolbar)
		self.caLayout.addWidget(self.caCanvas)

		self.advancedTabs.addTab(self.caWidget, "CA")

		self.angles2Widget = QtWidgets.QWidget(self.advancedTabs)
		self.angles2Widget.setObjectName("angles2Widget")

		self.angles2Layout = QtWidgets.QGridLayout(self.angles2Widget)
		self.angles2Layout.setObjectName("angles2Layout")
		self.angles2Layout.setContentsMargins(0, 0, 0, 0)

		self.angles2Figure = plt.figure()
		self.angles2Canvas = FigureCanvas(self.angles2Figure)
		self.angles2Toolbar = NavigationToolbar(self.angles2Canvas, self.angles2Widget)
		self.angles2Layout.addWidget(self.angles2Toolbar)
		self.angles2Layout.addWidget(self.angles2Canvas)

		self.advancedTabs.addTab(self.angles2Widget, "Angles 2")

		self.textOutput = QtWidgets.QTextEdit(self.splitter)
		self.textOutput.setObjectName("textOutput")

		self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

