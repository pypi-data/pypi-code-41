# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eric6/MicroPython/EspFirmwareSelectionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EspFirmwareSelectionDialog(object):
    def setupUi(self, EspFirmwareSelectionDialog):
        EspFirmwareSelectionDialog.setObjectName("EspFirmwareSelectionDialog")
        EspFirmwareSelectionDialog.resize(500, 114)
        EspFirmwareSelectionDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(EspFirmwareSelectionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(EspFirmwareSelectionDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.espComboBox = QtWidgets.QComboBox(EspFirmwareSelectionDialog)
        self.espComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.espComboBox.setObjectName("espComboBox")
        self.gridLayout.addWidget(self.espComboBox, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(EspFirmwareSelectionDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.firmwarePicker = E5PathPicker(EspFirmwareSelectionDialog)
        self.firmwarePicker.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.firmwarePicker.setObjectName("firmwarePicker")
        self.gridLayout.addWidget(self.firmwarePicker, 1, 1, 1, 2)
        self.addressLabel = QtWidgets.QLabel(EspFirmwareSelectionDialog)
        self.addressLabel.setObjectName("addressLabel")
        self.gridLayout.addWidget(self.addressLabel, 2, 0, 1, 1)
        self.addressEdit = E5ClearableLineEdit(EspFirmwareSelectionDialog)
        self.addressEdit.setMaxLength(4)
        self.addressEdit.setObjectName("addressEdit")
        self.gridLayout.addWidget(self.addressEdit, 2, 1, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(EspFirmwareSelectionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EspFirmwareSelectionDialog)
        self.buttonBox.accepted.connect(EspFirmwareSelectionDialog.accept)
        self.buttonBox.rejected.connect(EspFirmwareSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EspFirmwareSelectionDialog)
        EspFirmwareSelectionDialog.setTabOrder(self.espComboBox, self.firmwarePicker)
        EspFirmwareSelectionDialog.setTabOrder(self.firmwarePicker, self.addressEdit)

    def retranslateUi(self, EspFirmwareSelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        EspFirmwareSelectionDialog.setWindowTitle(_translate("EspFirmwareSelectionDialog", "Flash MicroPython Firmware"))
        self.label.setText(_translate("EspFirmwareSelectionDialog", "ESP Chip Type:"))
        self.espComboBox.setToolTip(_translate("EspFirmwareSelectionDialog", "Select the ESP chip type"))
        self.label_2.setText(_translate("EspFirmwareSelectionDialog", "Firmware:"))
        self.firmwarePicker.setToolTip(_translate("EspFirmwareSelectionDialog", "Enter the path of the firmware file"))
        self.addressLabel.setText(_translate("EspFirmwareSelectionDialog", "Address:"))
        self.addressEdit.setToolTip(_translate("EspFirmwareSelectionDialog", "Enter the flash addres in the hexadecimal form"))
from E5Gui.E5LineEdit import E5ClearableLineEdit
from E5Gui.E5PathPicker import E5PathPicker
