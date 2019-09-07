# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eric6/Preferences/ConfigurationPages/IconsPreviewDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IconsPreviewDialog(object):
    def setupUi(self, IconsPreviewDialog):
        IconsPreviewDialog.setObjectName("IconsPreviewDialog")
        IconsPreviewDialog.resize(596, 541)
        IconsPreviewDialog.setSizeGripEnabled(True)
        self.vboxlayout = QtWidgets.QVBoxLayout(IconsPreviewDialog)
        self.vboxlayout.setObjectName("vboxlayout")
        self.iconView = QtWidgets.QListWidget(IconsPreviewDialog)
        self.iconView.setMovement(QtWidgets.QListView.Free)
        self.iconView.setFlow(QtWidgets.QListView.LeftToRight)
        self.iconView.setGridSize(QtCore.QSize(100, 50))
        self.iconView.setViewMode(QtWidgets.QListView.IconMode)
        self.iconView.setObjectName("iconView")
        self.vboxlayout.addWidget(self.iconView)
        self.buttonBox = QtWidgets.QDialogButtonBox(IconsPreviewDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(IconsPreviewDialog)
        self.buttonBox.accepted.connect(IconsPreviewDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(IconsPreviewDialog)

    def retranslateUi(self, IconsPreviewDialog):
        _translate = QtCore.QCoreApplication.translate
        IconsPreviewDialog.setWindowTitle(_translate("IconsPreviewDialog", "Icons Preview"))
