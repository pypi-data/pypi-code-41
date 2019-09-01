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
import re
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .about import AboutWindow
from .new import NewWindow
from .settings import SettingsWindow
from .editor import EditorWindow

from ..manager import ProjectManager

from ..formats.formatException import UnsupportedFormatException
from ..systems.systemException import ProjectNotFoundSystemException

class ProjectManagerWindow(QMainWindow):
    _instance = None

    @staticmethod
    def getInstance():
        if ProjectManagerWindow._instance == None:
            ProjectManagerWindow._instance = ProjectManagerWindow()
        return ProjectManagerWindow._instance

    def __init__(self):
        super().__init__()
        self.initUI()
        _instance = self

    def initUI(self):
        center = QDesktopWidget().availableGeometry().center()
        self.setGeometry(center.x()-400, center.y()-300, 800, 600)
        self.setWindowTitle(self.tr('Offlate Project Manager'))
        self.projectManagerWidget = ProjectManagerWidget(self)
        self.setCentralWidget(self.projectManagerWidget)

    # Can be called from the editor window
    def new(self):
        self.projectManagerWidget.new()

class ProjectManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = ProjectManager()
        self.editor = EditorWindow(parent, self.manager)
        self.threadpool = QThreadPool()
        self.initUI()

    def initUI(self):
        # Manager Window UI: left is project list with options, right
        # is a set of actions

        hbox = QHBoxLayout()
        project_vbox = QVBoxLayout()
        self.searchfield = QLineEdit()
        project_vbox.addWidget(self.searchfield)
        self.projectlist = QListWidget()
        for p in self.manager.listProjects():
            item = QListWidgetItem(p['name'])
            item.setData(Qt.UserRole, p)
            self.projectlist.addItem(item)
        project_vbox.addWidget(self.projectlist)

        buttonbox = QHBoxLayout()
        self.open_button = QPushButton(self.tr("Open"))
        self.edit_button = QPushButton(self.tr("Edit"))
        self.remove_button = QPushButton(self.tr("Remove"))
        buttonbox.addWidget(self.open_button)
        buttonbox.addWidget(self.edit_button)
        buttonbox.addWidget(self.remove_button)

        project_vbox.addLayout(buttonbox)
        hbox.addLayout(project_vbox, 1)

        new_button = QPushButton(self.tr("New Project"))
        settings_button = QPushButton(self.tr("Settings"))
        about_button = QPushButton(self.tr("About Offlate"))
        quit_button = QPushButton(self.tr("Exit"))

        filename = os.path.dirname(__file__) + '/../icon.png'
        icon = QPixmap(filename)
        iconlabel = QLabel(self)
        iconlabel.setPixmap(icon)
        iconlabel.setAlignment(Qt.AlignCenter)

        global_vbox = QVBoxLayout()
        global_vbox.addSpacing(28)
        global_vbox.addWidget(new_button)
        global_vbox.addWidget(settings_button)
        global_vbox.addWidget(about_button)
        global_vbox.addStretch(1)
        global_vbox.addWidget(iconlabel)
        global_vbox.addStretch(1)
        global_vbox.addWidget(quit_button)

        hbox.addLayout(global_vbox, 1)

        self.setLayout(hbox)
        self.parent().statusBar()
        self.actionLabel = QLabel()
        self.actionProgress = QProgressBar()
        self.actionProgress.setEnabled(False)
        self.parent().statusBar().addWidget(self.actionLabel)
        self.parent().statusBar().addWidget(self.actionProgress)

        # Actions
        self.searchfield.textChanged.connect(self.filter)

        quit_button.clicked.connect(qApp.quit)
        new_button.clicked.connect(self.new)
        settings_button.clicked.connect(self.settings)
        about_button.clicked.connect(self.about)
        self.projectlist.currentItemChanged.connect(self.activate)
        self.remove_button.clicked.connect(self.remove)
        self.edit_button.clicked.connect(self.edit)
        self.open_button.clicked.connect(self.open)

        # Defaults
        self.edit_button.setEnabled(False)
        self.open_button.setEnabled(False)
        self.remove_button.setEnabled(False)

    def activate(self):
        self.edit_button.setEnabled(True)
        self.open_button.setEnabled(True)
        self.remove_button.setEnabled(True)

    def about(self):
        geometry = self.parent().geometry()
        w = AboutWindow()
        w.setGeometry(geometry.x() + geometry.width()/2 - 300,
                geometry.y() + geometry.height()/2 - 200,
                300, 200)
        w.exec_()

    def new(self):
        w = NewWindow(self.manager)
        w.exec_()
        if not w.wantNew():
            return
        res = self.manager.isConfigured(w.getProjectSystem())
        if not res:
            res = self.configureSystem(w.getProjectSystem())
        if not res:
            return
        worker = NewRunnable(self, w.getProjectName(), w.getProjectLang(),
                w.getProjectSystem(), w.getProjectInfo())
        worker.signals.finished.connect(self.openProject)
        worker.signals.finished.connect(self.finishReport)
        worker.signals.progress.connect(self.reportProgress)
        worker.signals.restart_required.connect(self.restartNew)
        self.threadpool.start(worker)

    def restartNew(self, name, lang, system, info, error):
        self.reportError(name, error)
        w = NewWindow(self.manager, self, name, lang, system, info)
        w.exec_()
        if not w.wantNew():
            return
        res = self.manager.isConfigured(w.getProjectSystem())
        if not res:
            res = self.configureSystem(w.getProjectSystem())
        if not res:
            return
        worker = NewRunnable(self, w.getProjectName(), w.getProjectLang(),
                w.getProjectSystem(), w.getProjectInfo())
        worker.signals.finished.connect(self.openProject)
        worker.signals.finished.connect(self.finishReport)
        worker.signals.progress.connect(self.reportProgress)
        worker.signals.restart_required.connect(self.restartNew)
        self.threadpool.start(worker)

    def configureSystem(self, system):
        w = SettingsWindow(self.manager.getConf(), system)
        w.exec_()
        if w.done:
            self.manager.updateSettings(w.data)
            return True
        return False

    def reportError(self, name, msg):
        dialog = QMessageBox()
        dialog.setText(msg)
        dialog.exec_()
        self.finishReport(name)

    def reportProgress(self, name, progress):
        self.actionProgress.setEnabled(True)
        self.actionProgress.setValue(progress)
        self.actionLabel.setText(
                self.tr('Fetching project {}...').format(name, progress))
        self.editor.actionProgress.setEnabled(True)
        self.editor.actionProgress.setValue(progress)
        self.editor.actionLabel.setText(
                self.tr('Fetching project {}...').format(name, progress))

    def finishReport(self, name):
        self.actionProgress.setValue(0)
        self.actionProgress.setEnabled(False)
        self.actionLabel.setText("")
        self.editor.actionProgress.setValue(0)
        self.editor.actionLabel.setText("")
        self.editor.actionProgress.setEnabled(False)

    def settings(self):
        w = SettingsWindow(self.manager.getConf())
        w.exec_()
        if w.done:
            self.manager.updateSettings(w.data)

    def filter(self):
        search = self.searchfield.text()
        self.projectlist.clear()
        regexp = re.compile(".*"+search)
        for p in self.manager.listProjects():
            if regexp.match(p['name']):
                item = QListWidgetItem(p['name'])
                item.setData(Qt.UserRole, p)
                self.projectlist.addItem(item)

    def open(self):
        item = self.projectlist.currentItem()
        data = item.data(Qt.UserRole)
        name = data['name']
        self.openProject(name)
        return ""

    def openProject(self, name):
        self.editor.show()
        self.parent().hide()
        self.editor.open(name)

    def remove(self):
        item = self.projectlist.currentItem()
        data = item.data(Qt.UserRole)
        name = data['name']
        self.manager.remove(name)
        self.filter()

    def edit(self):
        item = self.projectlist.currentItem()
        data = item.data(Qt.UserRole)
        name = data['name']

        w = NewWindow(self.manager, name=name, lang=data['lang'],
                system=data['system'], info=data['info'])
        w.exec_()
        if not w.wantNew():
            return
        worker = EditRunnable(self, w.getProjectName(), w.getProjectLang(),
                w.getProjectSystem(), w.getProjectInfo())
        worker.signals.progress.connect(self.reportProgress)
        worker.signals.restart_required.connect(self.restartNew)
        worker.signals.finished.connect(self.finishReport)
        self.threadpool.start(worker)

class NewRunnableSignals(QObject):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str, int)
    error = pyqtSignal(str, str)
    restart_required = pyqtSignal(str, str, int, dict, str)

class RunnableCallback:
    def progress(self, amount):
        if int(round(amount)) > self.oldamount:
            self.oldamount = int(round(amount))
            self.signals.progress.emit(self.name, amount)

    def project_exists(self):
        self.error = self.parent.tr('A project with the same name already exists. \
The new project was not created. You should first remove the same-named project.')

    def project_present(self, directory):
        self.error = self.parent.tr('Your filesystem contains a same-named \
directory for your new project. The new project was not created. You should \
first remove the same-named directory: "{}".'.format(directory))

    def project_error(self, error):
        if isinstance(error, UnsupportedFormatException):
            self.error = self.parent.tr('The project you added uses the {} format, \
but it is not supported yet by Offlate. You can try to update the application, \
or if you are on the latest version already, report it as a bug.'.format(error.unsupportedFormat))
        elif isinstance(error, ProjectNotFoundSystemException):
            self.error = self.parent.tr('The project {} you added could not be found \
in the translation platform you selected. Did you make a typo while entering the \
name or other parameters?'.format(error.projectNotFound))
        else:
            self.error = self.parent.tr('An unexpected error occured while \
fetching the project: {}. You should report this as a bug.'.format(str(error)))

class NewRunnable(QRunnable, RunnableCallback):
    def __init__(self, parent, name, lang, system, info):
        super().__init__()
        self.name = name
        self.lang = lang
        self.system = system
        self.info = info
        self.parent = parent
        self.signals = NewRunnableSignals()
        self.oldamount = -1
        self.error = None

    def run(self):
        res = self.parent.manager.createProject(self.name, self.lang, self.system,
                self.info, self)
        if res:
            self.signals.finished.emit(self.name)
        else:
            self.signals.restart_required.emit(self.name, self.lang, self.system,
                    self.info, self.error)
        self.parent.filter()

class EditRunnable(QRunnable, RunnableCallback):
    def __init__(self, parent, name, lang, system, info):
        super().__init__()
        self.name = name
        self.lang = lang
        self.system = system
        self.info = info
        self.parent = parent
        self.signals = NewRunnableSignals()
        self.oldamount = -1
        self.error = None

    def run(self):
        res = self.parent.manager.updateProject(self.name, self.lang, self.system,
                self.info, self)
        if res:
            self.signals.finished.emit(self.name)
        else:
            self.signals.restart_required.emit(self.name, self.lang, self.system,
                    self.info, self.error)
        self.parent.filter()
