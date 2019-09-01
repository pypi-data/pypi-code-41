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

class MultipleLineEdit(QWidget):
    textChanged = pyqtSignal()

    def __init__(self, parent = None):
        super(MultipleLineEdit, self).__init__(parent)
        self.initUI()

    def setText(self, texts):
        self.treeWidget.clear()
        items = []
        for text in texts:
            item = QTreeWidgetItem([text])
            items.append(item)
        self.treeWidget.insertTopLevelItems(0, items)

    def addLine(self, args):
        text = self.newtext.text()
        items = [QTreeWidgetItem([text])]
        self.treeWidget.insertTopLevelItems(0, items)

    def deleteLine(self, args):
        self.treeWidget.takeTopLevelItem(self.treeWidget.currentIndex().row())

    def content(self):
        number = self.treeWidget.topLevelItemCount()
        items = []
        for i in range(0, number):
            items.append(self.treeWidget.topLevelItem(i).text(0))
        return items

    def initUI(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.setLayout(vbox)
        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(1)
        vbox.addWidget(self.treeWidget)
        self.newtext = QLineEdit()
        addbutton = QPushButton(self.tr("Add"))
        addbutton.clicked.connect(self.addLine)
        removebutton = QPushButton(self.tr("Remove"))
        removebutton.clicked.connect(self.deleteLine, 0)
        hbox.addWidget(self.newtext)
        hbox.addWidget(addbutton)
        hbox.addWidget(removebutton)
        vbox.addLayout(hbox)
