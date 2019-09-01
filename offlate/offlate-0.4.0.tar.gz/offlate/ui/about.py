#   Copyright (c) 2019 Julien Lepiller <julien@lepiller.eu>
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

import os
import webbrowser

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class AboutWindow(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        filename = os.path.dirname(__file__) + '/../icon.png'
        icon = QPixmap(filename)
        label = QLabel(self)
        label.setPixmap(icon)
        label.setAlignment(Qt.AlignCenter)
        name = QLabel(self)
        name.setText("Offlate")
        font = name.font()
        font.setPointSize(64)
        font.setBold(True)
        name.setFont(font)

        explain = QLabel(self)
        explain.setText(self.tr("Offlate is a translation interface \
for offline translation of projects using online platforms. Offlate is free \
software, you can redistribute it under the GPL v3 license or any later version."))
        explain.setWordWrap(True)

        copyright = QLabel(self)
        copyright.setText(self.tr("Copyright (C) 2018, 2019 Julien Lepiller"))

        issue_button = QPushButton(self.tr("Report an issue"))
        ok_button = QPushButton(self.tr("Close this window"))

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(name)
        vbox.addWidget(explain)
        vbox.addWidget(copyright)
        vbox.addWidget(issue_button)
        vbox.addWidget(ok_button)

        self.setGeometry(10, 10, 300, 200)
        self.setLayout(vbox)

        # Actions
        ok_button.clicked.connect(self.close)
        issue_button.clicked.connect(self.issue)

    def issue(self):
        webbrowser.open('https://framagit.org/tyreunom/offlate/issues')
