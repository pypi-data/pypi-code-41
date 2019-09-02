#!/usr/bin/env python

import configparser
import platform
import os
import keyring

from pathlib import Path, PurePath

class Configuration():

    def __init__(self):

        config = configparser.ConfigParser()
        config.optionxform = str

        # Le chemin du fichier de configuration dépend du système d'exploitation
        self.configFilePath = self.getConfigFilePath()

        # Si le fichier de configuration n'existe pas, on le crée

        if not Path(self.configFilePath).exists():
            self.createConfigFile(self.configFilePath)

        # On charge les informations
        config.read(self.configFilePath)

        self._parameters = config
        self._password = keyring.get_password('DeclaTravaux', os.getlogin())

    def __getitem__(self, key):

        if key in ('PremierLancement', 'RepertoireDeclarations', 'RepertoireRecherche'):
            return self._parameters['Configuration'][key]

        elif key in ('AdresseElectronique', 'ServeurSMTP', 'PortServeurSMTP', 'NomExpediteur'):
            return self._parameters['Courriels'][key]

    def __setitem__(self, key, value):
        self.parameters = {key: value}

    def getConfigFilePath(self):
        """
        Retourne le chemin du fichier de configuration de l'application
        """
        cheminFichier = ''

        # Le chemin du fichier de configuration dépend du système d'exploitation
        if platform.system() == 'Linux':

            try:
                configDir = os.environ['XDG_CONFIG_HOME']
            except KeyError:
                configDir = PurePath(Path.home(), '.config/')
                #os.path.join(os.path.expanduser('~'), '.config')
            finally:
                configFilePath = PurePath(configDir, 'declaTravaux', 'declaTravaux.conf')
                #os.path.join(configDir, 'declaTravaux', 'declaTravaux.conf')

        elif platform.system() == 'Windows':
            configFilePath = PurePath(os.environ['AppData'], 'DeclaTravaux', 'DeclaTravaux.conf')
            #os.path.join(os.environ['AppData'], 'DeclaTravaux', 'DeclaTravaux.conf')

        return configFilePath

    def createConfigFile(self, filePath):
        """
        Fonction créant le fichier de configuration par défaut
        """

        config = configparser.ConfigParser()
        config.optionxform = str

        workDir = Path(Path.home(), 'Documents', 'DéclaTravaux')
        #workDir = os.path.join(os.path.expanduser('~'), 'Documents', 'DéclaTravaux')

        # Par défaut, les archives sont recherchées dans le répertoire « Téléchargements »
        # Si ce dernier n'est pas trouvé, elles sont recherchées dans le dossier de l'utilisateur
        if platform.system() == 'Linux':

            try:
                searchDir = Path(os.environ['XDG_DOWNLOAD_DIR'])

            except KeyError:
                searchDir = Path(Path.home(), 'Téléchargements')
                #os.path.join(os.path.expanduser('~'), 'Téléchargements')

                if not searchDir.exists():
                #if not os.path.isdir(searchDir):
                    searchDir = Path.home()
                    #os.path.expanduser('~')

        elif platform.system() == 'Windows':
            searchDir = Path(Path.home(), 'Downloads')
            #os.path.join(os.path.expanduser('~'), 'Downloads')


        config['Configuration'] = {'PremierLancement': '1',
                                    'RepertoireDeclarations': str(workDir),
                                    'RepertoireRecherche': str(searchDir)}

        config['Courriels'] = { 'AdresseElectronique': '',
                                'ServeurSMTP': '',
                                'PortServeurSMTP': '',
                                'NomExpediteur': ''}


        #os.makedirs(os.path.dirname(filePath), exist_ok=True)
        Path(filePath.parent).mkdir(exist_ok=True)

        with open(filePath, 'w') as configFile:
            config.write(configFile)

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, paramDict):

        config = self._parameters

        # Le paramètre PremierLancement est automatiquement affecté de la valeur 0
        config['Configuration']['PremierLancement'] = '0'

        # On boucle les paramètres donnés en arguments
        # S'ils correspondent aux paramètres attendus, on modifie les paramètres
        for parameter, value in paramDict.items():

            if parameter in ('RepertoireDeclarations', 'RepertoireRecherche'):

                config['Configuration'][parameter] = value

            elif parameter in ( 'AdresseElectronique',
                                'ServeurSMTP', 'PortServeurSMTP', 'NomExpediteur'):

                config['Courriels'][parameter] = value

        # Le fichier de configuration est sauvegardé
        with open(self.configFilePath, 'w') as configFile:
            config.write(configFile)

        self._parameters = config

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        keyring.set_password('DeclaTravaux', os.getlogin(), value)
        self._password = value