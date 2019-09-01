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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .gitlabedit import GitlabEdit

class SettingsWindow(QDialog):
    def __init__(self, preferences, system = -1, parent = None):
        super().__init__(parent)
        self.data = preferences
        self.done = False
        self.system = system
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()

        tab = QTabWidget()
        self.addGenericTab(tab)
        self.addTPTab(tab)
        self.addTransifexTab(tab)
        self.addGitlabTab(tab)

        buttonbox = QHBoxLayout()
        cancel = QPushButton(self.tr("Cancel"))
        ok = QPushButton(self.tr("OK"))
        buttonbox.addWidget(cancel)
        buttonbox.addWidget(ok)

        vbox.addWidget(tab)
        vbox.addLayout(buttonbox)
        self.setLayout(vbox)
        cancel.clicked.connect(self.close)
        ok.clicked.connect(self.ok)

        tab.setCurrentIndex(self.system + 1)

    def addTransifexTab(self, tab):
        formBox = QGroupBox(self.tr("Transifex"))
        formLayout = QFormLayout()
        self.TransifexToken = QLineEdit()

        if not "Transifex" in self.data:
            self.data["Transifex"] = {}
        try:
            self.TransifexToken.setText(self.data["Transifex"]["token"])
        except Exception:
            pass

        self.TransifexToken.textChanged.connect(self.updateTransifex)
        label = QLabel(self.tr("You can get a token from <a href=\"#\">https://www.transifex.com/user/settings/api/</a>"))
        label.linkActivated.connect(self.openTransifex)
        label.setWordWrap(True)

        formLayout.addRow(QLabel(self.tr("Token:")), self.TransifexToken)
        formLayout.addRow(label)

        formBox.setLayout(formLayout)
        tab.addTab(formBox, "Transifex")

    def openTransifex(self):
        QDesktopServices().openUrl(QUrl("https://www.transifex.com/user/settings/api/"));

    def updateTransifex(self):
        self.data["Transifex"] = {}
        self.data["Transifex"]["token"] = self.TransifexToken.text()

    def addGenericTab(self, tab):
        formBox = QGroupBox(self.tr("Generic Settings"))
        formLayout = QFormLayout()
        self.genericFullname = QLineEdit()
        self.genericFullname.setPlaceholderText(self.tr("John Doe <john@doe.me>"))

        if not "Generic" in self.data:
            self.data["Generic"] = {}
        if 'fullname' in self.data['Generic']:
            self.genericFullname.setText(self.data["Generic"]["fullname"])

        formLayout.addRow(QLabel(self.tr("Full Name:")), self.genericFullname)

        self.genericFullname.textChanged.connect(self.updateGeneric)

        formBox.setLayout(formLayout)
        tab.addTab(formBox, self.tr("Generic"))

    def updateGeneric(self):
        self.data["Generic"] = {}
        self.data["Generic"]["fullname"] = self.genericFullname.text()

    def addTPTab(self, tab):
        formBox = QGroupBox(self.tr("Translation Project"))
        formLayout = QFormLayout()

        self.TPemail = QLineEdit()
        self.TPuser = QLineEdit()
        self.TPserver = QLineEdit()

        if not "TP" in self.data:
            self.data["TP"] = {}

        if 'email' in self.data['TP']:
            self.TPemail.setText(self.data["TP"]["email"])
        if 'user' in self.data['TP']:
            self.TPuser.setText(self.data["TP"]["user"])
        if 'server' in self.data['TP']:
            self.TPserver.setText(self.data["TP"]["server"])

        self.TPemail.textChanged.connect(self.updateTP)
        self.TPuser.textChanged.connect(self.updateTP)
        self.TPserver.textChanged.connect(self.updateTP)

        formLayout.addRow(QLabel(self.tr("Email:")), self.TPemail)
        formLayout.addRow(QLabel(self.tr("Server:")), self.TPserver)
        formLayout.addRow(QLabel(self.tr("User Name:")), self.TPuser)

        formBox.setLayout(formLayout)
        tab.addTab(formBox, "TP")

    def updateTP(self):
        self.data["TP"] = {}
        self.data["TP"]["email"] = self.TPemail.text()
        self.data["TP"]["user"] = self.TPuser.text()
        self.data["TP"]["server"] = self.TPserver.text()

    def ok(self):
        self.done = True
        self.close()

    def addGitlabTab(self, tab):
        formBox = QGroupBox(self.tr("Gitlab"))
        formLayout = QVBoxLayout()
        label = QLabel(self.tr("Add your gitlab account tokens below. You need \
to create a token for every gitlab server you have an account on. You can create \
a token by logging into your account, going to your settings and in the Access \
Token page."))
        label.setWordWrap(True)
        formLayout.addWidget(label)

        if not "Gitlab" in self.data:
            self.data["Gitlab"] = {}

        self.gitlabEdit = GitlabEdit()
        for server in self.data["Gitlab"]["servers"]:
            self.gitlabEdit.addLine(server["server"], server["token"])

        formLayout.addSpacing(8)
        formLayout.addWidget(self.gitlabEdit)
        self.gitlabEdit.textChanged.connect(self.updateGitlab)

        formBox.setLayout(formLayout)
        tab.addTab(formBox, "Gitlab")

    def updateGitlab(self):
        if not "Gitlab" in self.data:
            self.data["Gitlab"] = {}
        self.data["Gitlab"]["servers"] = self.gitlabEdit.content()
