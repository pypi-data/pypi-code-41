#!/usr/bin/env python

import time
from pathlib import Path, PurePath

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from DeclaTravaux.ui_main_window import Ui_Main_Window
from DeclaTravaux import images_rc

from DeclaTravaux.configuration import Configuration
from DeclaTravaux.archives import Archives, Declaration
from DeclaTravaux.transmission_process import TransmissionProcess

class MainWindow(QMainWindow, Ui_Main_Window):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Chargement du fichier de configuration
        self.cfg = Configuration()

        # Masquage de la fenêtre « À Propos »
        fixAbout = self.textBrowserAbout.sizePolicy()
        fixAbout.setRetainSizeWhenHidden(True)
        self.textBrowserAbout.setSizePolicy(fixAbout)
        self.textBrowserAbout.setProperty('visible', False)

        # Masquage du bouton « Précédent » au démarrage
        self.pushButtonPrevious.setProperty('visible', False)

        # Remplissage du formulaire « Paramètres »
        self.fillParameters()

        # Ajout d'un validator sur lineEditFileSelection
        validator = QtGui.QRegExpValidator(QtCore.QRegExp('(.:)?.*/[0-9]{13}[A-Z]{1}([0-9][0-9])?_(DT|DICT|DDC|ATU).zip'), self.lineEditFile)
        self.lineEditFile.setValidator(validator)

        # Masquage de la ligne d'erreur
        fixFileError = self.labelFileError.sizePolicy()
        fixFileError.setRetainSizeWhenHidden(True)
        self.labelFileError.setSizePolicy(fixFileError)
        self.labelFileError.setProperty('visible', False)

        # S'il s'agit du premier lancement du logiciel,
        # le bouton « Démarrer » est désactivé
        if int(self.cfg['PremierLancement']):
            self.pushButtonNext.setEnabled(False)

        # Connexion des signaux vers les slots
        self.pushButtonAbout.toggled.connect(self.toggleAbout)

        self.pushButtonQuit.clicked.connect(self.close)
        self.pushButtonParameters.clicked.connect(self.showParameters)
        self.pushButtonPrevious.clicked.connect(self.goPrevious)
        self.pushButtonNext.clicked.connect(self.goNext)

        self.pushButtonSearchDir.clicked.connect(self.browseParameters)
        self.pushButtonWorkDir.clicked.connect(self.browseParameters)
        self.pushButtonParamCancel.clicked.connect(self.quitParameters)
        self.pushButtonParamValidate.clicked.connect(self.quitParameters)

        self.pushButtonBrowse.clicked.connect(self.browse)
        self.lineEditFile.textEdited.connect(self.checkFileFormat)
        self.listWidget.itemSelectionChanged.connect(lambda: self.activateButtonNext(True))

    # Méthode assignant les icônes
    def setWinIcon(self, pushButton, iconName):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f':/icons/icons/{iconName}.svg'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        pushButton.setIcon(icon)


    # Méthode affichant la page suivante
    def goNext(self):

        currentPage = self.stackedWidget.currentWidget()


        # Si la page actuelle est la page d'accueil
        # On lance la recherche d'archives
        # La page suivante dépend du résultat de la recherche
        if currentPage is self.pageStart:

            archives = Archives()
            self.archivesList = archives.search(self.cfg['RepertoireRecherche'])

            # S'il n'y a aucune archive trouvée,
            # la page suivante est pageFileSelection
            if len(self.archivesList) == 0:
                self.pushButtonNext.setEnabled(False)
                self.lineEditFile.setText('')
                self.stackedWidget.setCurrentWidget(self.pageFileSelection)

            # Si une seule archive est trouvée,
            # la page suivante est pageConfirmation
            elif len(self.archivesList) == 1:
                self.declaration = self.archivesList[0]
                self.setLabelConfirmation(self.declaration.dType, self.declaration.numero, self.declaration.date)
                self.stackedWidget.setCurrentWidget(self.pageConfirmation)

            # Si plusieurs archives sont trouvées,
            # le widget Liste est rempli
            # la page suivante est pageArchiveChoose
            else:

                # La liste est remplie selon les archives trouvées
                self.listWidget.clear()

                for declaration in self.archivesList:
                    self.listWidget.addItem(declaration.name)

                self.pushButtonNext.setEnabled(False)
                self.stackedWidget.setCurrentWidget(self.pageArchiveChoose)

            # Dans tous les cas, on masque le bouton « Paramètres »,
            # on affiche le bouton « Précédent »
            # et le bouton « Démarrer » est modifié en « Suivant »
            self.pushButtonParameters.setProperty('visible', False)
            self.pushButtonPrevious.setProperty('visible', True)
            self.pushButtonNext.setText('Suivant')


        elif currentPage in (self.pageFileSelection, self.pageArchiveChoose):

            # Si la page actuelle est pageFileSelection,
            # la page suivante est pageConfirmation
            if currentPage is self.pageFileSelection:
                if self.lineEditFile.hasAcceptableInput():
                    self.declaration = Declaration(self.lineEditFile.text())
                    self.stackedWidget.setCurrentWidget(self.pageConfirmation)
                else:
                    return 0

            # Si la page actuelle est pageArchiveChoose
            # la page suivante est pageConfirmation
            elif currentPage is self.pageArchiveChoose:
                self.declaration = self.archivesList[self.listWidget.currentRow()]
                self.stackedWidget.setCurrentWidget(self.pageConfirmation)

            self.setLabelConfirmation(self.declaration.dType, self.declaration.numero, self.declaration.date)

        # Si la page actuelle est pageConfirmation,
        # la page suivante est pageProgress
        elif currentPage is self.pageConfirmation:
            self.stackedWidget.setCurrentWidget(self.pageProgress)

            # Les différents boutons sont masqués
            self.pushButtonQuit.setProperty('visible', False)
            self.pushButtonPrevious.setProperty('visible', False)
            self.pushButtonNext.setProperty('visible', False)

            # Boucle sur la barre de progression
            i = 0
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(5)

            errorType, errorText = False, False

            for step in TransmissionProcess(self.declaration):

                if type(step) is tuple:
                    errorType, errorText = step
                    break

                self.labelStep.setText(step + '...')
                self.progressBar.setValue(i)
                i += 1

            # Une fois le traitement terminé,
            # la dernière page est affichée

            if errorType:
                self.labelEndIcon.setPixmap(QtGui.QPixmap(":/images/cancel.svg"))
                self.labelEnd1.setText('La déclaration n’a pas été télétransmise.')
                self.labelEnd1.setStyleSheet('color: rgb(226,87,76);')
                self.labelEnd2.setText(errorText)
                self.labelEnd2.setStyleSheet('color: rgb(226,87,76);')
                self.pushButtonNext.setText('Réessayer')
                icon = QtGui.QIcon.fromTheme('edit-redo')

            else:
                self.labelEndIcon.setPixmap(QtGui.QPixmap(":/images/checked.svg"))
                self.labelEnd1.setText('La déclaration a été télétransmise.')
                self.labelEnd1.setStyleSheet('color: rgb(61, 179, 158);')
                self.labelEnd2.setText(f'Un courriel récapitulatif a été envoyé à {self.cfg["AdresseElectronique"]}.')
                self.labelEnd2.setStyleSheet('color: rgb(61, 179, 158);')
                self.pushButtonNext.setText('Nouvelle déclaration')
                icon = QtGui.QIcon.fromTheme('document-new')

            self.stackedWidget.setCurrentWidget(self.pageEnd)
            self.pushButtonQuit.setProperty('visible', True)
            self.pushButtonNext.setIcon(icon)
            self.pushButtonNext.setProperty('visible', True)

        # Si la page actuelle est pageEnd,
        # la page d'accueil est affichée
        elif currentPage is self.pageEnd:
            self.stackedWidget.setCurrentWidget(self.pageStart)
            self.pushButtonNext.setText('Démarrer')
            icon = QtGui.QIcon.fromTheme('go-next')
            self.pushButtonNext.setIcon(icon)
            self.pushButtonParameters.setProperty('visible', True)

        else:
            self.stackedWidget.setCurrentIndex((self.stackedWidget.currentIndex()+1) % self.stackedWidget.count())

    #  Méthode affichant la page précédente
    def goPrevious(self):

        currentPage = self.stackedWidget.currentWidget()

        # Si la page actuelle est pageSelection ou pageArchiveChoose,
        # la page précédente est pageStart
        if currentPage in (self.pageFileSelection, self.pageArchiveChoose):

            self.stackedWidget.setCurrentWidget(self.pageStart)
            self.pushButtonNext.setEnabled(True)
            self.lineEditFile.setText('')
            self.listWidget.clear()

            # Masquage bouton Précédent / Affichage bouton Paramètres
            # Bouton Suivant renommé en Démarrer
            self.pushButtonPrevious.setProperty('visible', False)
            self.pushButtonParameters.setProperty('visible', True)
            self.pushButtonNext.setText('Démarrer')

        # Si la page actuelle est pageConfirmation,
        # la page précédente dépend du nombre d'archives qui avaient été trouvées
        elif currentPage is self.pageConfirmation:
            pages = {0: self.pageFileSelection, 1: self.pageStart, 2: self.pageArchiveChoose}
            self.stackedWidget.setCurrentWidget(pages.get(len(self.archivesList), self.pageArchiveChoose))

            if len(self.archivesList) == 1:
                self.pushButtonPrevious.setProperty('visible', False)
                self.pushButtonParameters.setProperty('visible', True)

        else:
            self.stackedWidget.setCurrentIndex((self.stackedWidget.currentIndex()-1) % self.stackedWidget.count())

    # Affichage des paramètres
    def showParameters(self):
        self.stackedWidget.setCurrentWidget(self.pageParameters)
        self.stackedWidgetButtons.setCurrentWidget(self.stackedWidgetButtonsParameters)

    # Validation ou annulation des paramètres
    def quitParameters(self):

        # Si le bouton Valider est appelé,
        # on enregistre les paramètres
        if self.sender().objectName() == 'pushButtonParamValidate':

            self.cfg.parameters = {'RepertoireRecherche': self.lineEditSearchDir.text(),
                                    'RepertoireDeclarations': self.lineEditWorkDir.text(),
                                    'AdresseElectronique': self.lineEditMail.text(),
                                    'ServeurSMTP': self.lineEditSmtpServer.text(),
                                    'PortServeurSMTP': self.lineEditSmtpPort.text(),
                                    'NomExpediteur': self.lineEditExpeditorName.text(),
                                    }
            self.cfg.password = self.lineEditPassword.text()

            self.pushButtonNext.setEnabled(True)

        # Si le bouton Annuler est appelé,
        # les anciens paramètres sont restaurés dans le formulaire
        else:
            self.fillParameters()

        self.stackedWidget.setCurrentWidget(self.pageStart)
        self.stackedWidgetButtons.setCurrentWidget(self.stackedWidgetButtonsDefault)

    def toggleAbout(self):
        state = self.textBrowserAbout.property('visible')
        self.textBrowserAbout.setProperty('visible', not state)

    def browse(self):
        (fileUrl, f) = QFileDialog.getOpenFileName(self, 'Choisir une archive', '~/', 'Archives (*.zip);;Tous les fichiers (*)')
        if fileUrl:
            self.lineEditFile.setText(fileUrl)
            self.checkFileFormat()

    def browseParameters(self):
        directoryUrl = QFileDialog.getExistingDirectory(self, 'Choisir un répertoire', str(Path().home()), QFileDialog.ShowDirsOnly)
        if directoryUrl:
            if self.sender().objectName() == 'pushButtonSearchDir':
                self.lineEditSearchDir.setText(directoryUrl)
            else:
                self.lineEditWorkDir.setText(directoryUrl)

    def activateButtonNext(self, boolean):
        self.pushButtonNext.setEnabled(boolean)

    def checkFileFormat(self):
        if not self.lineEditFile.hasAcceptableInput() or not Path(self.lineEditFile.text()).exists():
            self.lineEditFile.setStyleSheet('color: rgb(226,87,76);')
            self.labelFileError.setProperty('visible', True)
            self.activateButtonNext(False)

            if not self.lineEditFile.hasAcceptableInput():
                self.labelFileError.setText('Le format de l’archive sélectionnée est incorrect.')
            else:
                self.labelFileError.setText('Le fichier indiqué n’existe pas.')

        else:
            self.lineEditFile.setStyleSheet('')
            self.labelFileError.setProperty('visible', False)
            self.activateButtonNext(True)

    def fillParameters(self):
        self.lineEditSearchDir.setText(self.cfg['RepertoireRecherche'])
        self.lineEditWorkDir.setText(self.cfg['RepertoireDeclarations'])
        self.lineEditMail.setText(self.cfg['AdresseElectronique'])
        self.lineEditPassword.setText(self.cfg.password)
        self.lineEditSmtpServer.setText(self.cfg['ServeurSMTP'])
        self.lineEditSmtpPort.setText(self.cfg['PortServeurSMTP'])
        self.lineEditExpeditorName.setText(self.cfg['NomExpediteur'])

    def setLabelConfirmation(self, dType, numero, date):

        det = 'L’' if dType == 'ATU' else 'La '

        self.labelConfirmation.setText(f"""
                    <style>
                    p {{margin: 15px; line-height: 125%; font-size: 14pt; text-align: center}};
                    b {{white-space: nowrap;}}
                    </style>
                    <p>
                        {det}<b>{dType}</b> n<span style="vertical-align: super;">o</span>
                        <b>{numero}</b> du <b>{date.replace(' ', '&nbsp;')}</b> a été sélectionnée.
                    </p>
                    <p>
                        Souhaitez-vous procéder à sa télétransmission ?
                    </p>""")