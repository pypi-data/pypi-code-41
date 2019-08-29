from PySide2 import QtWidgets, QtCore, QtGui
from annotation import Annotation
from library import Library
from superposition import Superposition
from decomposition import Decomposition
import os

class Ui_Aleph(object):
	def setupUI(self, Aleph):
		
		Aleph.setObjectName("MainWindow")
		Aleph.setWindowTitle("ALEPH (2019-08-08)")

		self.centralWidget = QtWidgets.QWidget(Aleph)
		self.centralWidget.setObjectName("centralWidget")

		self.centralWidgetLayout = QtWidgets.QGridLayout(self.centralWidget)
		self.centralWidgetLayout.setObjectName("centralWidgetLayout")
		self.centralWidgetLayout.setContentsMargins(11, 11, 11, 11)
		self.centralWidgetLayout.setSpacing(6)

		self.toolBar = QtWidgets.QToolBar(Aleph)
		self.toolBar.setObjectName("toolBar")
		self.toolBar.setMovable(False)
		Aleph.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

		self.actionOpen = QtWidgets.QAction(Aleph)
		self.actionOpen.setObjectName("actionOpen")
		self.actionOpen.setText("Open")
		self.toolBar.addAction(self.actionOpen)

		self.actionSave = QtWidgets.QAction(Aleph)
		self.actionSave.setObjectName("actionSave")
		self.actionSave.setText("Save")
		self.actionSave.setEnabled(False)
		self.toolBar.addAction(self.actionSave)

		self.actionMenu = QtWidgets.QAction(Aleph)
		self.actionMenu.setObjectName("actionMenu")
		self.actionMenu.setText("Menu")
		self.actionMenu.setEnabled(False)
		self.toolBar.addAction(self.actionMenu)

		self.actionSettings = QtWidgets.QAction(Aleph)
		self.actionSettings.setObjectName("actionSettings")
		self.actionSettings.setText("Settings")
		self.toolBar.addAction(self.actionSettings)	

		spacer = QtWidgets.QWidget()
		spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding);
		self.toolBar.addWidget(spacer);

		self.runButton = QtWidgets.QPushButton(Aleph)
		self.runButton.setText("RUN")

		self.actionRun = QtWidgets.QWidgetAction(Aleph)
		self.actionRun.setObjectName("actionRun")
		self.actionRun.setDefaultWidget(self.runButton)
		self.actionRun.setEnabled(False)
		self.toolBar.addAction(self.actionRun);

		self.stopButton = QtWidgets.QPushButton(Aleph)
		self.stopButton.setText("STOP")

		self.actionStop = QtWidgets.QWidgetAction(Aleph)
		self.actionStop.setObjectName("actionStop")
		self.actionStop.setDefaultWidget(self.stopButton)
		self.actionStop.setEnabled(False)
		self.toolBar.addAction(self.actionStop);

		self.statusBar = QtWidgets.QStatusBar(Aleph)
		self.statusBar.setObjectName("statusBar")
		Aleph.setStatusBar(self.statusBar)

		self.stackedWidget = QtWidgets.QStackedWidget(self.centralWidget)
		self.stackedWidget.setObjectName("stackedWidget")
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
		self.stackedWidget.setSizePolicy(sizePolicy)

		self.start = QtWidgets.QWidget(self.centralWidget)
		self.start.setObjectName("start")

		self.startLayout = QtWidgets.QGridLayout(self.start)
		self.startLayout.setObjectName("startLayout")
		self.startLayout.setContentsMargins(11, 11, 11, 11)
		self.startLayout.setSpacing(6)

		self.libraryDoc = QtGui.QTextDocument(self.start)
		self.libraryButton = QtWidgets.QPushButton(self.start)
		self.libraryButton.setObjectName("libraryButton")
		self.startLayout.addWidget(self.libraryButton, 1, 0, 1, 1)

		self.decompositionDoc = QtGui.QTextDocument(self.start)
		self.decompositionButton = QtWidgets.QPushButton(self.start)
		self.decompositionButton.setObjectName("decompositionButton")
		self.startLayout.addWidget(self.decompositionButton, 0, 1, 1, 1)
		
		self.superpositionDoc = QtGui.QTextDocument(self.start)
		self.superpositionButton = QtWidgets.QPushButton(self.start)
		self.superpositionButton.setObjectName("superpositionButton")
		self.startLayout.addWidget(self.superpositionButton, 1, 1, 1, 1)
		
		self.annotationDoc = QtGui.QTextDocument(self.start)
		self.annotationButton = QtWidgets.QPushButton(self.start)
		self.annotationButton.setObjectName("annotationButton")
		self.startLayout.addWidget(self.annotationButton, 0, 0, 1, 1)

		self.stackedWidget.addWidget(self.start)

		self.library = Library(Aleph)
		self.library.setObjectName("library")
		self.stackedWidget.addWidget(self.library)

		self.decomposition = Decomposition(Aleph)
		self.decomposition.setObjectName("decomposition")
		self.stackedWidget.addWidget(self.decomposition)

		self.superposition = Superposition(Aleph)
		self.superposition.setObjectName("superposition")
		self.stackedWidget.addWidget(self.superposition)

		self.annotation = Annotation(Aleph)
		self.annotation.setObjectName("annotation")
		self.stackedWidget.addWidget(self.annotation)

		self.stackedWidget.setCurrentIndex(0)
		self.centralWidgetLayout.addWidget(self.stackedWidget, 0, 1, 1, 1)

		Aleph.setCentralWidget(self.centralWidget)

	def paintMainWindow(self):

		settings = QtCore.QSettings()
		font = settings.value("font_size")

		self.runButton.setStyleSheet("QPushButton:enabled{background-color: rgb(0, 255, 0); color: black;} QPushButton:hover{background-color: rgb(0, 179, 0);}")
		self.stopButton.setStyleSheet("QPushButton:enabled{background-color: rgb(255, 0, 0); color: black;} QPushButton:hover{background-color: rgb(179, 0, 0);}")
		self.library.ui.tabs.setStyleSheet("QTabWidget::pane { border: 0; }");
		self.annotation.ui.tabs.setStyleSheet("QTabWidget::pane { border: 0; }");
		self.decomposition.ui.tabs.setStyleSheet("QTabWidget::pane { border: 0; }");
		self.superposition.ui.tabs.setStyleSheet("QTabWidget::pane { border: 0; }");

		self.libraryDoc.setHtml("<p align=center><font size=\""+str(6+(int(font)-10))+"\"><b>Library generation</b></font><br/><br/><br/><font size=\""+str(3+(int(font)-10))+"\">Define, extract, cluster and superpose libraries of local folds</font><br/><br/><br/></p><img src=\""+os.path.join(os.path.dirname(__file__),"img/library.png")+"\"></img>");
		#self.libraryDoc.setTextWidth(self.libraryDoc.size().width());
		self.libraryDoc.setTextWidth(550);
		libraryPixmap = QtGui.QPixmap(self.libraryDoc.size().width(), self.libraryDoc.size().height())
		libraryPixmap.fill( QtCore.Qt.transparent );
		libraryPainter = QtGui.QPainter(libraryPixmap)
		self.libraryDoc.drawContents(libraryPainter);
		self.libraryButton.setIconSize(libraryPixmap.size());
		self.libraryButton.setIcon(QtGui.QIcon(libraryPixmap));
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.libraryButton.sizePolicy().hasHeightForWidth())
		self.libraryButton.setSizePolicy(sizePolicy)
		libraryPainter.end()		

		self.decompositionDoc.setHtml("<p align=center><font size=\""+str(6+(int(font)-10))+"\"><b>Decomposition</b></font><br/><br/><br/><font size=\""+str(3+(int(font)-10))+"\">Cluster secondary structure elements into compact rigid groups</font><br/><br/><br/></p><img src=\""+os.path.join(os.path.dirname(__file__),"img/decomposition.png")+"\"></img>");
		#self.decompositionDoc.setTextWidth(self.decompositionDoc.size().width());
		self.decompositionDoc.setTextWidth(550);
		decompositionPixmap = QtGui.QPixmap(self.decompositionDoc.size().width(), self.decompositionDoc.size().height())
		decompositionPixmap.fill( QtCore.Qt.transparent );
		decompositionPainter = QtGui.QPainter(decompositionPixmap)
		self.decompositionDoc.drawContents(decompositionPainter);
		self.decompositionButton.setIconSize(decompositionPixmap.size());
		self.decompositionButton.setIcon(QtGui.QIcon(decompositionPixmap));
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.decompositionButton.sizePolicy().hasHeightForWidth())
		self.decompositionButton.setSizePolicy(sizePolicy)
		decompositionPainter.end()

		self.superpositionDoc.setHtml("<p align=center><font size=\""+str(6+(int(font)-10))+"\"><b>Superposition</b></font><br/><br/><br/><font size=\""+str(3+(int(font)-10))+"\">Superpose a library of fragments into a model</font><br/><br/><br/></p><img src=\""+os.path.join(os.path.dirname(__file__),"img/superposition.png")+"\"></img>");
		#self.superpositionDoc.setTextWidth(self.superpositionDoc.size().width());
		self.superpositionDoc.setTextWidth(550);
		superpositionPixmap = QtGui.QPixmap(self.superpositionDoc.size().width(), self.superpositionDoc.size().height())
		superpositionPixmap.fill( QtCore.Qt.transparent );
		superpositionPainter = QtGui.QPainter(superpositionPixmap)
		self.superpositionDoc.drawContents(superpositionPainter);
		self.superpositionButton.setIconSize(superpositionPixmap.size());
		self.superpositionButton.setIcon(QtGui.QIcon(superpositionPixmap));
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.superpositionButton.sizePolicy().hasHeightForWidth())
		self.superpositionButton.setSizePolicy(sizePolicy)
		superpositionPainter.end()

		self.annotationDoc.setHtml("<p align=center><font size=\""+str(6+(int(font)-10))+"\"><b>Secondary structure annotation</b></font><br/><br/><br/><font size=\""+str(3+(int(font)-10))+"\">Identify archetypal secondary structures through geometrical descriptors</font><br/><br/><br/></p><img src=\""+os.path.join(os.path.dirname(__file__),"img/annotation.png")+"\"></img>");		#self.annotationDoc.setTextWidth(self.annotationDoc.size().width());
		self.annotationDoc.setTextWidth(550);
		annotationPixmap = QtGui.QPixmap(self.annotationDoc.size().width(), self.annotationDoc.size().height())
		annotationPixmap.fill( QtCore.Qt.transparent );
		annotationPainter = QtGui.QPainter(annotationPixmap)
		self.annotationDoc.drawContents(annotationPainter);
		self.annotationButton.setIconSize(annotationPixmap.size());
		self.annotationButton.setIcon(QtGui.QIcon(annotationPixmap));
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.annotationButton.sizePolicy().hasHeightForWidth())
		self.annotationButton.setSizePolicy(sizePolicy)
		annotationPainter.end()

