# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eric6/MicroPython/CircuitPythonFirmwareSelectionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CircuitPythonFirmwareSelectionDialog(object):
    def setupUi(self, CircuitPythonFirmwareSelectionDialog):
        CircuitPythonFirmwareSelectionDialog.setObjectName("CircuitPythonFirmwareSelectionDialog")
        CircuitPythonFirmwareSelectionDialog.resize(500, 124)
        CircuitPythonFirmwareSelectionDialog.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(CircuitPythonFirmwareSelectionDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.boardComboBox = QtWidgets.QComboBox(CircuitPythonFirmwareSelectionDialog)
        self.boardComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.boardComboBox.setObjectName("boardComboBox")
        self.gridLayout.addWidget(self.boardComboBox, 1, 1, 1, 1)
        self.firmwarePicker = E5PathPicker(CircuitPythonFirmwareSelectionDialog)
        self.firmwarePicker.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.firmwarePicker.setObjectName("firmwarePicker")
        self.gridLayout.addWidget(self.firmwarePicker, 0, 1, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(339, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(CircuitPythonFirmwareSelectionDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(CircuitPythonFirmwareSelectionDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(CircuitPythonFirmwareSelectionDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.bootPicker = E5PathPicker(CircuitPythonFirmwareSelectionDialog)
        self.bootPicker.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.bootPicker.setObjectName("bootPicker")
        self.gridLayout.addWidget(self.bootPicker, 2, 1, 1, 3)
        self.buttonBox = QtWidgets.QDialogButtonBox(CircuitPythonFirmwareSelectionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 4)
        self.retestButton = QtWidgets.QToolButton(CircuitPythonFirmwareSelectionDialog)
        self.retestButton.setEnabled(False)
        self.retestButton.setObjectName("retestButton")
        self.gridLayout.addWidget(self.retestButton, 1, 2, 1, 1)

        self.retranslateUi(CircuitPythonFirmwareSelectionDialog)
        self.buttonBox.accepted.connect(CircuitPythonFirmwareSelectionDialog.accept)
        self.buttonBox.rejected.connect(CircuitPythonFirmwareSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CircuitPythonFirmwareSelectionDialog)
        CircuitPythonFirmwareSelectionDialog.setTabOrder(self.firmwarePicker, self.boardComboBox)
        CircuitPythonFirmwareSelectionDialog.setTabOrder(self.boardComboBox, self.retestButton)
        CircuitPythonFirmwareSelectionDialog.setTabOrder(self.retestButton, self.bootPicker)

    def retranslateUi(self, CircuitPythonFirmwareSelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        CircuitPythonFirmwareSelectionDialog.setWindowTitle(_translate("CircuitPythonFirmwareSelectionDialog", "Flash CircuitPython Firmware"))
        self.boardComboBox.setToolTip(_translate("CircuitPythonFirmwareSelectionDialog", "Select the board type or \'Manual\'"))
        self.firmwarePicker.setToolTip(_translate("CircuitPythonFirmwareSelectionDialog", "Enter the path of the CircuitPython firmware file"))
        self.label_3.setText(_translate("CircuitPythonFirmwareSelectionDialog", "Firmware:"))
        self.label_2.setText(_translate("CircuitPythonFirmwareSelectionDialog", "Boot Path:"))
        self.label.setText(_translate("CircuitPythonFirmwareSelectionDialog", "Board Type:"))
        self.bootPicker.setToolTip(_translate("CircuitPythonFirmwareSelectionDialog", "Enter the path to the device in bootloader mode"))
        self.retestButton.setToolTip(_translate("CircuitPythonFirmwareSelectionDialog", "Press to search the selected volume"))
from E5Gui.E5PathPicker import E5PathPicker
