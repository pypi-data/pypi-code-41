# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eric6/Plugins/VcsPlugins/vcsMercurial/QueuesExtension/HgQueuesHeaderDialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_HgQueuesHeaderDialog(object):
    def setupUi(self, HgQueuesHeaderDialog):
        HgQueuesHeaderDialog.setObjectName("HgQueuesHeaderDialog")
        HgQueuesHeaderDialog.resize(400, 300)
        HgQueuesHeaderDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(HgQueuesHeaderDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.messageEdit = QtWidgets.QPlainTextEdit(HgQueuesHeaderDialog)
        self.messageEdit.setReadOnly(True)
        self.messageEdit.setObjectName("messageEdit")
        self.verticalLayout.addWidget(self.messageEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(HgQueuesHeaderDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(HgQueuesHeaderDialog)
        QtCore.QMetaObject.connectSlotsByName(HgQueuesHeaderDialog)
        HgQueuesHeaderDialog.setTabOrder(self.messageEdit, self.buttonBox)

    def retranslateUi(self, HgQueuesHeaderDialog):
        _translate = QtCore.QCoreApplication.translate
        HgQueuesHeaderDialog.setWindowTitle(_translate("HgQueuesHeaderDialog", "Commit Message"))
