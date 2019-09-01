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

import json
import os
import re
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ..systems.list import *
from ..formats.list import *
from .multiplelineedit import MultipleLineEdit

class NewWindow(QDialog):
    def __init__(self, manager, parent = None, name = "", 
            lang = "", system = 0, info = None):
        super().__init__(parent)
        self.name = name
        self.lang = lang
        self.system = system
        self.info = info
        self.manager = manager
        self.askNew = False
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout()
        predefinedbox = QVBoxLayout()
        self.searchfield = QLineEdit()
        predefinedbox.addWidget(self.searchfield)
        self.predefinedprojects = QListWidget()
        with open(os.path.dirname(__file__) + '/../data.json') as f:
            self.projectdata = json.load(f)
            for d in self.projectdata:
                item = QListWidgetItem(d['name'])
                item.setData(Qt.UserRole, d)
                self.predefinedprojects.addItem(item)
        predefinedbox.addWidget(self.predefinedprojects)

        contentbox = QVBoxLayout()
        formbox = QGroupBox(self.tr("Project information"))
        self.formLayout = QFormLayout()
        formbox.setLayout(self.formLayout)

        self.nameWidget = QLineEdit()
        self.nameWidget.setText(self.name)
        self.langWidget = QLineEdit()
        self.langWidget.setText(self.lang)
        self.formLayout.addRow(QLabel(self.tr("Name:")), self.nameWidget)
        self.formLayout.addRow(QLabel(self.tr("Target Language:")), self.langWidget)
        self.combo = QComboBox()
        self.combo.addItem(self.tr("The Translation Project"))
        self.combo.addItem(self.tr("Transifex"))
        self.combo.addItem(self.tr("Gitlab"))
        self.combo.setCurrentIndex(self.system)
        self.formLayout.addRow(self.combo)

        self.nameWidget.textChanged.connect(self.modify)
        self.langWidget.textChanged.connect(self.modify)

        hhbox = QHBoxLayout()
        self.cancelbutton = QPushButton(self.tr("Cancel"))
        self.okbutton = QPushButton(self.tr("OK"))
        self.okbutton.setEnabled(False)
        hhbox.addWidget(self.cancelbutton)
        hhbox.addWidget(self.okbutton)
        contentbox.addWidget(formbox)
        contentbox.addLayout(hhbox)
        hbox.addLayout(predefinedbox)
        hbox.addLayout(contentbox)

        self.additionalFields = []
        self.additionalFields.append([])
        self.additionalFields.append([])
        self.additionalFields.append([])
        
        # Transifex
        self.transifexOrganisation = QLineEdit()
        if self.system == TRANSIFEX:
            self.transifexOrganisation.setText(self.info['organization'])
        self.transifexOrganisation.textChanged.connect(self.modify)
        transifexOrganisationLabel = QLabel(self.tr("Organization"))
        self.additionalFields[TRANSIFEX].append({'label': transifexOrganisationLabel,
            'widget': self.transifexOrganisation})

        # Gitlab
        self.gitlabRepo = QLineEdit()
        self.gitlabRepo.textChanged.connect(self.modify)
        gitlabRepoLabel = QLabel(self.tr('repository'))
        self.additionalFields[GITLAB].append({'label': gitlabRepoLabel,
            'widget': self.gitlabRepo})
        self.gitlabBranch = QLineEdit()
        self.gitlabBranch.textChanged.connect(self.modify)
        gitlabBranchLabel = QLabel(self.tr('branch'))
        self.additionalFields[GITLAB].append({'label': gitlabBranchLabel,
            'widget': self.gitlabBranch})
        if self.system == GITLAB:
            self.gitlabRepo.setText(self.info['repo'])
            self.gitlabBranch.setText(self.info['branch'])

        self.setLayout(hbox)

        self.predefinedprojects.currentItemChanged.connect(self.fill)
        self.cancelbutton.clicked.connect(self.close)
        self.okbutton.clicked.connect(self.ok)
        self.searchfield.textChanged.connect(self.filter)
        self.combo.currentIndexChanged.connect(self.othersystem)
        self.modify()
        self.othersystem()

    def ok(self):
        self.askNew = True
        self.close()

    def fill(self):
        item = self.predefinedprojects.currentItem()
        data = item.data(Qt.UserRole)
        self.nameWidget.setText(data['name'])
        self.combo.setCurrentIndex(int(data['system']))
        if data['system'] == TRANSIFEX:
            self.transifexOrganisation.setText(data['organisation'])
        if data['system'] == GITLAB:
            self.gitlabRepo.setText(data['repo'])
            self.gitlabBranch.setText(data['branch'])

    def filter(self):
        search = self.searchfield.text()
        self.predefinedprojects.clear()
        regexp = re.compile(".*"+search)
        for d in self.projectdata:
            if regexp.match(d['name']):
                item = QListWidgetItem(d['name'])
                item.setData(Qt.UserRole, d)
                self.predefinedprojects.addItem(item)

    def modify(self):
        enable = False
        if self.nameWidget.text() != '' and self.langWidget.text() != '':
            enable = True
            for widget in self.additionalFields[self.combo.currentIndex()]:
                if isinstance(widget['widget'], QLineEdit) and widget['widget'].text() == '':
                    enable = False
                    break
        self.okbutton.setEnabled(enable)

    def wantNew(self):
        return self.askNew

    def getProjectName(self):
        return self.nameWidget.text()

    def getProjectLang(self):
        return self.langWidget.text()

    def getProjectSystem(self):
        return self.combo.currentIndex()

    def getProjectInfo(self):
        if self.getProjectSystem() == TRANSLATION_PROJECT:
            return {}
        if self.getProjectSystem() == TRANSIFEX:
            return {'organization': self.additionalFields[TRANSIFEX][0]['widget'].text()}
        if self.getProjectSystem() == GITLAB:
            return {'repo': self.additionalFields[GITLAB][0]['widget'].text(),
                    'branch': self.additionalFields[GITLAB][1]['widget'].text()}
        return {}

    def othersystem(self):
        for system in self.additionalFields:
            for widget in system:
                self.formLayout.takeRow(widget['widget'])
                widget['widget'].hide()
                widget['label'].hide()
        self.formLayout.invalidate()
        oldwidget = self.combo
        for widget in self.additionalFields[self.combo.currentIndex()]:
            self.setTabOrder(oldwidget, widget['widget'])
            oldwidget = widget['widget']
            self.formLayout.addRow(widget['label'], widget['widget'])
            widget['widget'].show()
            widget['label'].show()
        self.setTabOrder(oldwidget, self.cancelbutton)
        self.setTabOrder(self.cancelbutton, self.okbutton)
        self.modify()
