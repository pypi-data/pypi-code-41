from PySide2 import QtWidgets, QtCore, QtGui
import os
from ui_settings import Ui_Settings

class Settings(QtWidgets.QDialog):
	def __init__(self):
		super().__init__()
		self.ui = Ui_Settings()
		self.ui.setupUI(self)
		self.settings = QtCore.QSettings()
		self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"img/icon.png")))		
		self.init_ui()
		
	def init_ui(self):
		self.ui.pathLoad.clicked.connect(self.load_path)
		self.ui.cootLoad.clicked.connect(self.coot_path)
		self.ui.buttonBox.accepted.connect(self.ok_clicked)
		self.ui.buttonBox.rejected.connect(self.cancel_clicked)
		self.ui.minAhValue.valueChanged.connect(self.min_ah_changed)
		self.ui.maxAhValue.valueChanged.connect(self.max_ah_changed)
		self.ui.minBsValue.valueChanged.connect(self.min_bs_changed)
		self.ui.maxBsValue.valueChanged.connect(self.max_bs_changed)

		self.ui.pathLine.setText(self.settings.value("aleph_path"))
		self.ui.cootLine.setText(self.settings.value("coot_path"))
		self.ui.peptideValue.setValue(int(self.settings.value("peptide_length")))
		self.ui.fontValue.setValue(int(self.settings.value("font_size")))
		self.ui.widthValue.setValue(int(self.settings.value("width_pic")))
		self.ui.heightValue.setValue(int(self.settings.value("height_pic")))
		self.ui.minAhValue.setValue(int(self.settings.value("min_ah_dist")))
		self.ui.maxAhValue.setValue(int(self.settings.value("max_ah_dist")))
		self.ui.minBsValue.setValue(int(self.settings.value("min_bs_dist")))
		self.ui.maxBsValue.setValue(int(self.settings.value("max_bs_dist")))
		self.ui.graphmlCheck.setChecked(int(self.settings.value("write_graphml")))
		self.ui.showValue.setCurrentText(self.settings.value("color"))

	def ok_clicked(self):
		self.settings.setValue("aleph_path", self.ui.pathLine.text())
		self.settings.setValue("coot_path", self.ui.cootLine.text())
		self.settings.setValue("font_size", self.ui.fontValue.value())
		self.settings.setValue("peptide_length", self.ui.peptideValue.value())
		self.settings.setValue("width_pic", self.ui.widthValue.value())
		self.settings.setValue("height_pic", self.ui.heightValue.value())
		self.settings.setValue("min_ah_dist", self.ui.minAhValue.value())
		self.settings.setValue("max_ah_dist", self.ui.maxAhValue.value())
		self.settings.setValue("min_bs_dist", self.ui.minBsValue.value())
		self.settings.setValue("max_bs_dist", self.ui.maxBsValue.value())
		self.settings.setValue("write_graphml", self.ui.graphmlCheck.checkState())
		self.settings.setValue("color", self.ui.showValue.currentText())
		self.close()

	def cancel_clicked(self):
		self.close()

	def load_path(self):
		options = QtWidgets.QFileDialog.Options()
		path, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select ALEPH path", "","", options=options)
		if path:
			self.ui.pathLine.setText(path)		

	def coot_path(self):
		options = QtWidgets.QFileDialog.Options()
		path, _ = QtWidgets.QFileDialog.getOpenFileName(None,"Select coot path", "","", options=options)
		if path:
			self.ui.cootLine.setText(path)

	def min_ah_changed(self, value):
		if value > self.ui.maxAhValue.value():
			self.ui.minAhValue.setValue(self.ui.maxAhValue.value())

	def max_ah_changed(self, value):
		if value < self.ui.minAhValue.value():
			self.ui.maxAhValue.setValue(self.ui.minAhValue.value())

	def min_bs_changed(self, value):
		if value > self.ui.maxBsValue.value():
			self.ui.minBsValue.setValue(self.ui.maxBsValue.value())

	def max_bs_changed(self, value):
		if value < self.ui.minBsValue.value():
			self.ui.maxBsValue.setValue(self.ui.minBsValue.value())