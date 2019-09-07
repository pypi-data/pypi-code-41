# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eric6/WebBrowser/Network/ProtocolHandlerManagerDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProtocolHandlerManagerDialog(object):
    def setupUi(self, ProtocolHandlerManagerDialog):
        ProtocolHandlerManagerDialog.setObjectName("ProtocolHandlerManagerDialog")
        ProtocolHandlerManagerDialog.resize(500, 400)
        ProtocolHandlerManagerDialog.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(ProtocolHandlerManagerDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.protocolHandlersList = QtWidgets.QTreeWidget(ProtocolHandlerManagerDialog)
        self.protocolHandlersList.setAlternatingRowColors(True)
        self.protocolHandlersList.setRootIsDecorated(False)
        self.protocolHandlersList.setObjectName("protocolHandlersList")
        self.gridLayout.addWidget(self.protocolHandlersList, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.deleteButton = QtWidgets.QPushButton(ProtocolHandlerManagerDialog)
        self.deleteButton.setObjectName("deleteButton")
        self.verticalLayout.addWidget(self.deleteButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ProtocolHandlerManagerDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)

        self.retranslateUi(ProtocolHandlerManagerDialog)
        self.buttonBox.accepted.connect(ProtocolHandlerManagerDialog.accept)
        self.buttonBox.rejected.connect(ProtocolHandlerManagerDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ProtocolHandlerManagerDialog)

    def retranslateUi(self, ProtocolHandlerManagerDialog):
        _translate = QtCore.QCoreApplication.translate
        ProtocolHandlerManagerDialog.setWindowTitle(_translate("ProtocolHandlerManagerDialog", "Protocol Handlers"))
        self.protocolHandlersList.setToolTip(_translate("ProtocolHandlerManagerDialog", "Shows a list of registered protocol handlers"))
        self.protocolHandlersList.headerItem().setText(0, _translate("ProtocolHandlerManagerDialog", "Scheme"))
        self.protocolHandlersList.headerItem().setText(1, _translate("ProtocolHandlerManagerDialog", "URL"))
        self.deleteButton.setToolTip(_translate("ProtocolHandlerManagerDialog", "Press to delete the protocol handler"))
        self.deleteButton.setText(_translate("ProtocolHandlerManagerDialog", "Delete"))
