# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eric6/VirtualEnv/VirtualenvInterpreterSelectionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VirtualenvInterpreterSelectionDialog(object):
    def setupUi(self, VirtualenvInterpreterSelectionDialog):
        VirtualenvInterpreterSelectionDialog.setObjectName("VirtualenvInterpreterSelectionDialog")
        VirtualenvInterpreterSelectionDialog.resize(550, 150)
        VirtualenvInterpreterSelectionDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(VirtualenvInterpreterSelectionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(VirtualenvInterpreterSelectionDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.nameEdit = QtWidgets.QLineEdit(VirtualenvInterpreterSelectionDialog)
        self.nameEdit.setReadOnly(True)
        self.nameEdit.setObjectName("nameEdit")
        self.horizontalLayout.addWidget(self.nameEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(VirtualenvInterpreterSelectionDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.pythonExecPicker = E5PathPicker(VirtualenvInterpreterSelectionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pythonExecPicker.sizePolicy().hasHeightForWidth())
        self.pythonExecPicker.setSizePolicy(sizePolicy)
        self.pythonExecPicker.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.pythonExecPicker.setObjectName("pythonExecPicker")
        self.verticalLayout.addWidget(self.pythonExecPicker)
        self.variantComboBox = QtWidgets.QComboBox(VirtualenvInterpreterSelectionDialog)
        self.variantComboBox.setObjectName("variantComboBox")
        self.variantComboBox.addItem("")
        self.variantComboBox.setItemText(0, "Python 3")
        self.variantComboBox.addItem("")
        self.variantComboBox.setItemText(1, "Python 2")
        self.verticalLayout.addWidget(self.variantComboBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(VirtualenvInterpreterSelectionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(VirtualenvInterpreterSelectionDialog)
        self.buttonBox.accepted.connect(VirtualenvInterpreterSelectionDialog.accept)
        self.buttonBox.rejected.connect(VirtualenvInterpreterSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(VirtualenvInterpreterSelectionDialog)
        VirtualenvInterpreterSelectionDialog.setTabOrder(self.pythonExecPicker, self.variantComboBox)
        VirtualenvInterpreterSelectionDialog.setTabOrder(self.variantComboBox, self.nameEdit)

    def retranslateUi(self, VirtualenvInterpreterSelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        VirtualenvInterpreterSelectionDialog.setWindowTitle(_translate("VirtualenvInterpreterSelectionDialog", "Add Virtual Environment"))
        self.label_2.setText(_translate("VirtualenvInterpreterSelectionDialog", "Name:"))
        self.label.setText(_translate("VirtualenvInterpreterSelectionDialog", "Enter interpreter for virtual environment:"))
        self.pythonExecPicker.setToolTip(_translate("VirtualenvInterpreterSelectionDialog", "Enter the Python interpreter of the virtual environment"))
        self.variantComboBox.setToolTip(_translate("VirtualenvInterpreterSelectionDialog", "Select the Python variant"))
from E5Gui.E5PathPicker import E5PathPicker
