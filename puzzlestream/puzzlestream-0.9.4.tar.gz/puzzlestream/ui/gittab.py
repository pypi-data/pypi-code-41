# -*- coding: utf-8 -*-
"""Git tab module.

contains PSGitTab, a subclass of QWidget
"""

from os import path, remove
from threading import Thread
from typing import Callable

from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.notificationsystem import newNotification
import puzzlestream.ui.colors as colors
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class PSGitTab(QWidget):

    def __init__(self, parent: QObject = None):
        super().__init__(parent=parent)
        self.__repo = None
        self.__layout = QGridLayout()
        self.__reloadSignal = PSSignal()
        self.__fileSaveSignal, self.__fileUpdateSignal = PSSignal(), PSSignal()
        self.setLayout(self.__layout)

        self.btnBranch = QPushButton()
        self.btnFetch = QPushButton()
        self.btnStageAll = QPushButton()
        self.btnUnstageAll = QPushButton()
        self.btnRevertAll = QPushButton()
        self.btnCommit = QPushButton()
        self.btnPullNPush = QPushButton()
        self.changedWidget = QWidget()
        self.stagedWidget = QWidget()
        self.lblCommitMessage = QLabel()
        self.fileListChanged = QListWidget()
        self.fileListStaged = QListWidget()
        self.txtCommitMessage = PSCommitMessageBox()

        self.lblChanged = QLabel()
        self.lblStaged = QLabel()
        self.btnStage = QPushButton()
        self.btnRevert = QPushButton()
        self.btnUnstage = QPushButton()
        self.__changedLayout = QHBoxLayout()
        self.__stagedLayout = QHBoxLayout()
        self.changedWidget.setLayout(self.__changedLayout)
        self.stagedWidget.setLayout(self.__stagedLayout)
        self.__changedLayout.addWidget(self.lblChanged)
        self.__changedLayout.addWidget(self.btnStage)
        self.__changedLayout.addWidget(self.btnRevert)
        self.__stagedLayout.addWidget(self.lblStaged)
        self.__stagedLayout.addWidget(self.btnUnstage)

        for btn in [self.btnFetch, self.btnStageAll, self.btnUnstageAll,
                    self.btnRevertAll, self.btnPullNPush]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setStyleSheet(
                "QPushButton { min-width: 1.25em; max-width: 1.25em; " +
                "min-height: 1.25em; max-height: 1.25em; " +
                "background-color: %s; }" % (colors.get("Qt-background"))
            )

        for btn in [self.btnStage, self.btnUnstage, self.btnRevert,
                    self.btnBranch]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setStyleSheet(
                "QPushButton { min-width: 1em; max-width: 1em; " +
                "min-height: 1em; max-height: 1em; " +
                "background-color: %s; }" % (colors.get("Qt-background"))
            )

        for btn in [self.btnCommit, self.changedWidget, self.stagedWidget,
                    self.lblCommitMessage]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.txtCommitMessage.setMinimumWidth(200)

        self.fileListChanged.setSelectionMode(QListWidget.ExtendedSelection)
        self.fileListStaged.setSelectionMode(QListWidget.ExtendedSelection)

        self.btnFetch.clicked.connect(self.fetch)
        self.btnStageAll.clicked.connect(self.stageAll)
        self.btnUnstageAll.clicked.connect(self.unstageAll)
        self.btnRevertAll.clicked.connect(self.revertAll)
        self.btnPullNPush.clicked.connect(self.pull)
        self.btnStage.clicked.connect(self.stage)
        self.btnUnstage.clicked.connect(self.unstage)
        self.btnRevert.clicked.connect(self.revert)
        self.btnCommit.clicked.connect(self.commit)
        self.fileListChanged.selectionModel().selectionChanged.connect(
            self.__changedSelectionChanged)
        self.fileListStaged.selectionModel().selectionChanged.connect(
            self.__stagedSelectionChanged)
        self.txtCommitMessage.textChanged.connect(self.__commitMessageChanged)
        self.txtCommitMessage.submitSignal.connect(self.commit)

        base = path.join(__file__, "../../icons/")
        self.btnStageAll.setIcon(QIcon(path.abspath(base + "plus.png")))
        self.btnUnstageAll.setIcon(QIcon(path.abspath(base + "minus.png")))
        self.btnRevertAll.setIcon(QIcon(path.abspath(base + "back_blue.png")))
        self.btnPullNPush.setIcon(QIcon(path.abspath(base + "pull_push.png")))
        self.btnStage.setIcon(QIcon(path.abspath(base + "plus.png")))
        self.btnUnstage.setIcon(QIcon(path.abspath(base + "minus.png")))
        self.btnRevert.setIcon(QIcon(path.abspath(base + "back_blue.png")))

        self.__layout.addWidget(self.btnBranch, 0, 0)
        self.__layout.addWidget(self.btnFetch, 1, 0)
        self.__layout.addWidget(self.btnStageAll, 2, 0)
        self.__layout.addWidget(self.btnUnstageAll, 3, 0)
        self.__layout.addWidget(self.btnRevertAll, 4, 0)
        self.__layout.addWidget(self.btnPullNPush, 5, 0)
        self.__layout.addWidget(self.changedWidget, 0, 1)
        self.__layout.addWidget(self.fileListChanged, 1, 1, 6, 1)
        self.__layout.addWidget(self.stagedWidget, 0, 2)
        self.__layout.addWidget(self.fileListStaged, 1, 2, 6, 1)
        self.__layout.addWidget(self.lblCommitMessage, 0, 3)
        self.__layout.addWidget(self.txtCommitMessage, 1, 3, 4, 1)
        self.__layout.addWidget(self.btnCommit, 5, 3)

        self.__fetchTimer = QTimer()
        self.__fetchTimer.setInterval(60000)
        self.__fetchTimer.timeout.connect(self.fetch)
        self.__fetchTimer.start()

        self.__pullThread = None
        self.__pullTimer = QTimer()
        self.__pullTimer.setInterval(50)
        self.__pullTimer.timeout.connect(self.__pullCallback)

        self.retranslateUi()

    def retranslateUi(self):
        if self.currentBranchHasRemote:
            self.btnFetch.setToolTip(translate("GitTab", "Fetch"))
        else:
            self.btnFetch.setToolTip(translate("GitTab", "Reload"))
        self.btnStageAll.setToolTip(translate("GitTab", "Stage all changes"))
        self.btnUnstageAll.setToolTip(
            translate("GitTab", "Unstage all changes"))
        self.btnRevertAll.setToolTip(translate("GitTab", "Revert all changes"))
        self.btnCommit.setText(translate("GitTab", "Commit"))
        self.btnPullNPush.setToolTip(translate("GitTab", "Pull and push"))
        self.lblCommitMessage.setToolTip(translate("GitTab", "Commit message"))

        self.lblChanged.setText(translate("GitTab", "Changed"))
        self.lblStaged.setText(translate("GitTab", "Staged changes"))
        self.btnStage.setToolTip(translate("GitTab", "Stage"))
        self.btnRevert.setToolTip(translate("GitTab", "Revert"))
        self.btnUnstage.setToolTip(translate("GitTab", "Unstage"))

    def changeEvent(self, event: QEvent):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    @property
    def reloadSignal(self) -> PSSignal:
        return self.__reloadSignal

    @property
    def fileSaveSignal(self) -> PSSignal:
        return self.__fileSaveSignal

    @property
    def fileUpdateSignal(self) -> PSSignal:
        return self.__fileUpdateSignal

    @property
    def numberOfChangedItems(self) -> int:
        return self.fileListChanged.count()

    @property
    def hasRemote(self) -> bool:
        if self.__repo is not None:
            try:
                return len(self.__repo.remotes) > 0
            except Exception as e:
                print(e)
                newNotification(
                    translate("GitTab", "Git error:") + " " + str(e))
                return False
        return False

    @property
    def currentBranchHasRemote(self) -> bool:
        if self.__repo is not None:
            try:
                return self.__repo.active_branch.tracking_branch() is not None
            except Exception as e:
                print(e)
                newNotification(
                    translate("GitTab", "Git error:") + " " + str(e))
        return False

    @property
    def activeBranchName(self) -> str:
        if self.__repo is not None:
            try:
                return self.__repo.active_branch.name
            except Exception as e:
                print(e)
                newNotification(
                    translate("GitTab", "Git error:") + " " + str(e))
        return translate("GitTab", "not available")

    def setRepo(self, repo):
        self.__repo = repo
        self.fetch()

    def reload(self):
        self.fileListChanged.clear()
        self.fileListStaged.clear()

        if self.__repo is not None:
            try:
                for f in self.__repo.untracked_files:
                    item = QListWidgetItem(f)
                    item.setBackground(QColor(colors.get("error")))
                    self.fileListChanged.addItem(item)

                for f in [item.a_path for item in self.__repo.index.diff(None)]:
                    item = QListWidgetItem(f)
                    item.setBackground(QColor(colors.get("running")))
                    self.fileListChanged.addItem(item)

                for f in [item.a_path for item in self.__repo.index.diff("HEAD")]:
                    self.fileListStaged.addItem(QListWidgetItem(f))

                for btn in [self.btnBranch, self.btnFetch, self.btnPullNPush,
                            self.btnCommit, self.btnRevertAll, self.btnStageAll,
                            self.btnUnstageAll]:
                    btn.setEnabled(True)

                if not self.currentBranchHasRemote:
                    self.btnPullNPush.setEnabled(False)
                    self.btnFetch.setToolTip(translate("GitTab", "Reload"))
                    self.btnFetch.setIcon(QIcon(path.abspath(
                        path.join(__file__, "../../icons/reload.png"))))
                else:
                    self.btnFetch.setToolTip(translate("GitTab", "Fetch"))
                    self.btnFetch.setIcon(QIcon(path.abspath(
                        path.join(__file__, "../../icons/fetch.png"))))

                    nAhead = len(list(self.__repo.iter_commits(
                        "%s@{u}..%s" % (self.__repo.active_branch,
                                        self.__repo.active_branch)))
                                 )
                    nBehind = len(list(self.__repo.iter_commits(
                        "%s..%s@{u}" % (self.__repo.active_branch,
                                        self.__repo.active_branch)))
                                  )
                    if (self.__pullThread is None or not
                            self.__pullThread.isAlive()):
                        self.btnPullNPush.setToolTip(
                            translate("GitTab", "Pull" + " (%d)" % (nBehind)))
                        self.btnPullNPush.setEnabled(nBehind > 0)
                    else:
                        self.btnPullNPush.setToolTip("Pulling...")
                        self.btnPullNPush.setEnabled(False)
                    # self.btnPush.setText("Push (%d)" % (nAhead))
                    # self.btnPush.setEnabled(nAhead > 0)
            except Exception as e:
                print(e)
                newNotification(
                    translate("GitTab", "Git error:") + " " + str(e))
        else:
            for btn in [self.btnFetch, self.btnPullNPush, self.btnCommit,
                        self.btnRevertAll, self.btnStageAll,
                        self.btnUnstageAll]:
                btn.setEnabled(False)

        self.__changedSelectionChanged()
        self.__stagedSelectionChanged()
        self.__commitMessageChanged()

        self.reloadSignal.emit()

    def fetch(self):
        if self.hasRemote:
            self.btnFetch.setToolTip("Fetching...")
            self.btnFetch.setEnabled(False)

            try:
                thr = CallbackThread(target=self.__repo.git.fetch,
                                     callback=self.__fetchCallback)
                thr.start()
            except Exception as e:
                print(e)
                newNotification(
                    translate("GitTab", "Git error:") + " " + str(e))
        else:
            self.reload()

    def __fetchCallback(self):
        self.reload()
        if self.currentBranchHasRemote:
            self.btnFetch.setToolTip(translate("GitTab", "Fetch"))
        else:
            self.btnFetch.setToolTip(translate("GitTab", "Reload"))
        self.btnFetch.setEnabled(True)

    def stageAll(self):
        try:
            self.__repo.git.add(".")
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))
        self.reload()

    def revertAll(self):
        if self.__confirmRevert(allChanges=True):
            try:
                for item in self.__repo.untracked_files:
                    remove(item)
                self.__repo.git.checkout(
                    "--",
                    *[item.a_path for item in self.__repo.index.diff(None)]
                )
            except Exception as e:
                print(e)
                newNotification(
                    translate("GitTab", "Git error:") + " " + str(e))
        self.reload()
        self.fileUpdateSignal.emit()
        self.fileSaveSignal.emit()

    def unstageAll(self):
        try:
            self.__repo.index.reset("HEAD")
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))
        self.reload()

    def stage(self):
        try:
            for item in self.fileListChanged.selectedItems():
                self.__repo.git.add(item.text())
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))
        self.reload()

    def revert(self):
        if self.__confirmRevert():
            reverts = []
            try:
                for item in self.fileListChanged.selectedItems():
                    if item.text() in self.__repo.untracked_files:
                        remove(item.text())
                    else:
                        reverts.append(item.text())
                self.__repo.git.checkout("--", *reverts)
            except Exception as e:
                print(e)
                newNotification(
                    translate("GitTab", "Git error:") + " " + str(e))
        self.reload()
        self.fileUpdateSignal.emit()
        self.fileSaveSignal.emit()

    def unstage(self):
        try:
            self.__repo.index.reset(
                "HEAD",
                paths=[item.text()
                       for item in self.fileListStaged.selectedItems()]
            )
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))
        self.reload()

    def commit(self):
        try:
            if (self.txtCommitMessage.toPlainText() != "" and
                    len(self.__repo.index.diff("HEAD")) > 0):
                self.__repo.index.commit(self.txtCommitMessage.toPlainText())
                self.txtCommitMessage.clear()
                self.reload()
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))

    def pullAndPush(self):
        self.pull()
        self.push()

    def pull(self):
        try:
            self.__pullThread = Thread(target=self.__pull)
            self.__pullThread.start()
            self.__pullTimer.start()
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))

    def __pull(self):
        self.fileSaveSignal.emit()
        try:
            self.__repo.git.pull()
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))

    def __pullCallback(self):
        if not self.__pullThread.isAlive():
            self.__pullTimer.stop()
            self.fileUpdateSignal.emit()
            self.reload()

    def push(self):
        self.btnPullNPush.setToolTip("Pushing...")
        self.btnPullNPush.setEnabled(False)

        try:
            thr = CallbackThread(target=self.__repo.git.push,
                                 callback=self.reload)
            thr.start()
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))

    def __changedSelectionChanged(self):
        enabled = len(self.fileListChanged.selectedIndexes()) != 0
        self.btnStage.setEnabled(enabled)
        self.btnRevert.setEnabled(enabled)

    def __stagedSelectionChanged(self):
        self.btnUnstage.setEnabled(
            len(self.fileListStaged.selectedIndexes()) != 0)

    def __commitMessageChanged(self):
        try:
            self.btnCommit.setEnabled(
                self.__repo is not None and
                self.txtCommitMessage.toPlainText() != "" and
                len(self.__repo.index.diff("HEAD")) > 0
            )
        except Exception as e:
            print(e)
            newNotification(translate("GitTab", "Git error:") + " " + str(e))

    def __confirmRevert(self, allChanges: bool = False):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Revert confirmation")
        if allChanges:
            msgBox.setText("Are you sure you want to revert all changes?")
        else:
            msgBox.setText(
                "Are you sure you want to revert the selected changes?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if msgBox.exec_() == QMessageBox.Yes:
            return True
        return False

    # def __updateBranchMenu(self):
    #     self.menuCheckout.clear()
    #     self.__menuCheckoutActions.clear()

    #     if self.__repo is not None:
    #         for h in self.__repo.heads:
    #             a = self.menuCheckout.addAction(h.name)
    #             a.triggered.connect(
    #                 lambda checked=False, n=h.name: self.__checkout(n))
    #             self.__menuCheckoutActions.append(a)

    #         a = self.menuCheckout.addAction("+ New branch")
    #         a.triggered.connect(self.__newBranch)
    #         self.__menuCheckoutActions.append(a)

    def __checkout(self, name: str):
        self.__repo.git.checkout(name)
        self.fetch()

    def __newBranch(self):
        print("new branch")


class CallbackThread(Thread):
    def __init__(self, callback: Callable = None, callback_args: tuple = (),
                 *args, **kwargs):
        target = kwargs.pop('target')
        super().__init__(target=self.target_with_callback, *args, **kwargs)
        self.callback = callback
        self.method = target
        self.callback_args = callback_args

    def target_with_callback(self):
        self.method()
        if self.callback is not None:
            self.callback(*self.callback_args)


class PSCommitMessageBox(QPlainTextEdit):

    def __init__(self, text: str = "", parent: QObject = None):
        self.__submitSignal = PSSignal()
        super().__init__(text, parent)

    @property
    def submitSignal(self) -> PSSignal:
        return self.__submitSignal

    def keyPressEvent(self, e: QEvent):
        if (e.key() in (Qt.Key_Return, Qt.Key_Enter) and
                (e.modifiers() and Qt.ControlModifier)):
            self.submitSignal.emit()
        return super().keyPressEvent(e)
