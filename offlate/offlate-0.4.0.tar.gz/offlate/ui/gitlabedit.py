#   Copyright (c) 2018 Julien Lepiller <julien@lepiller.eu>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
####

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class GitlabEdit(QWidget):
    textChanged = pyqtSignal()

    def __init__(self, parent = None):
        super(GitlabEdit, self).__init__(parent)
        self.initUI()

    def addLine(self, server, token):
        items = [QTreeWidgetItem([server, token])]
        self.treeWidget.addTopLevelItems(items)

    def addLineSlot(self):
        server = self.serverEdit.text()
        token = self.tokenEdit.text()
        items = [QTreeWidgetItem([server, token])]
        self.treeWidget.addTopLevelItems(items)
        self.textChanged.emit()

    def deleteLineSlot(self):
        self.treeWidget.takeTopLevelItem(self.treeWidget.currentIndex().row())
        self.textChanged.emit()

    def content(self):
        number = self.treeWidget.topLevelItemCount()
        items = []
        for i in range(0, number):
            item = self.treeWidget.topLevelItem(i)
            items.append({"server": item.text(0), "token": item.text(1)})
        return items

    def initUI(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.setLayout(vbox)
        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(2)
        vbox.addWidget(self.treeWidget)
        self.serverEdit = QLineEdit()
        self.serverEdit.setPlaceholderText(self.tr("server"))
        self.tokenEdit = QLineEdit()
        self.tokenEdit.setPlaceholderText(self.tr("token"))
        addbutton = QPushButton(self.tr("Add"))
        addbutton.clicked.connect(self.addLineSlot)
        removebutton = QPushButton(self.tr("Remove"))
        removebutton.clicked.connect(self.deleteLineSlot)
        hbox.addWidget(self.serverEdit)
        hbox.addWidget(self.tokenEdit)
        hbox.addWidget(addbutton)
        hbox.addWidget(removebutton)
        vbox.addLayout(hbox)
