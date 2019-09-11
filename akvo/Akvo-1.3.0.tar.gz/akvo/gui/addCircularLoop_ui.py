# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tirons/src/akvo/akvo/gui/addCircularLoop.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_circularLoopAdd(object):
    def setupUi(self, circularLoopAdd):
        circularLoopAdd.setObjectName("circularLoopAdd")
        circularLoopAdd.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(circularLoopAdd)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(circularLoopAdd)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.centreNorth = QtWidgets.QDoubleSpinBox(circularLoopAdd)
        self.centreNorth.setMinimum(-999999999.0)
        self.centreNorth.setMaximum(9999999999.0)
        self.centreNorth.setObjectName("centreNorth")
        self.gridLayout.addWidget(self.centreNorth, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(circularLoopAdd)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.centreEast = QtWidgets.QDoubleSpinBox(circularLoopAdd)
        self.centreEast.setMinimum(-99999999.0)
        self.centreEast.setMaximum(99999999.99)
        self.centreEast.setObjectName("centreEast")
        self.gridLayout.addWidget(self.centreEast, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(circularLoopAdd)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(circularLoopAdd)
        self.doubleSpinBox.setDecimals(3)
        self.doubleSpinBox.setMinimum(-99.0)
        self.doubleSpinBox.setProperty("value", -0.001)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout.addWidget(self.doubleSpinBox, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(circularLoopAdd)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(circularLoopAdd)
        self.doubleSpinBox_2.setMinimum(0.1)
        self.doubleSpinBox_2.setMaximum(299.99)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.gridLayout.addWidget(self.doubleSpinBox_2, 3, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(circularLoopAdd)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(circularLoopAdd)
        self.spinBox.setMinimum(5)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 4, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(circularLoopAdd)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 1)

        self.retranslateUi(circularLoopAdd)
        self.buttonBox.accepted.connect(circularLoopAdd.accept)
        self.buttonBox.rejected.connect(circularLoopAdd.reject)
        QtCore.QMetaObject.connectSlotsByName(circularLoopAdd)

    def retranslateUi(self, circularLoopAdd):
        _translate = QtCore.QCoreApplication.translate
        circularLoopAdd.setWindowTitle(_translate("circularLoopAdd", "Dialog"))
        self.label.setText(_translate("circularLoopAdd", "Centre Northing "))
        self.label_2.setText(_translate("circularLoopAdd", "Centre Easting"))
        self.label_3.setText(_translate("circularLoopAdd", "height "))
        self.doubleSpinBox.setToolTip(_translate("circularLoopAdd", "<html><head/><body><p>Akvo uses a positive down convention, a slight negative value to the loop height improves numerical stability using digital filtering hankel transforms. </p></body></html>"))
        self.label_4.setText(_translate("circularLoopAdd", "radius"))
        self.doubleSpinBox_2.setToolTip(_translate("circularLoopAdd", "<html><head/><body><p>Radius of the loop</p></body></html>"))
        self.label_5.setText(_translate("circularLoopAdd", "segments"))
        self.spinBox.setToolTip(_translate("circularLoopAdd", "<html><head/><body><p>Currently Akvo/Merlin calculates circular loops using segments of wire, forming a polygon. Analytic circular loops may be added in the future. </p></body></html>"))
