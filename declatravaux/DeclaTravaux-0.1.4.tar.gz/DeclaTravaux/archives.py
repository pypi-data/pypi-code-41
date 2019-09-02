#!/usr/bin/env python

import re
import os
import calendar

from pathlib import Path, PurePath

class Archives():

    def __init__(self):

        #On définit le format de fichier .zip attendu
        self.archiveRegex = re.compile(r'[0-9]{13}[A-Z]{1}([0-9][0-9])?_(DT|DICT|DDC|ATU).zip')
        self.archivesList = list()

    def search(self, searchDir):
        """
        Recherche, dans le répertoire indiqué en premier paramètre,
        les fichiers .zip dont les noms correspondent à l'expression régulière donnée en second paramètre.
        """
        if Path(searchDir).exists():
            # On liste les fichiers contenus dans le dossier de recherche
            filesList = Path(searchDir).iterdir()
            # On filtre la liste pour n'obtenir que les fichiers correspondant à l'expression régulière
            self.archivesList = [Declaration(f) for f in filesList if re.match(self.archiveRegex, f.name)]

            self.archivesList.sort(key=lambda declaration: declaration.fileName)

        return self.archivesList

class Declaration():

    def __init__(self, path):

        path = Path(path)

        self.fileName = path.name
        self.filePath = path.resolve()
        self.dType = self.getType(path)
        self.numero = self.getNumero(path)
        self.date = self.getDate(path)
        self.name = self.getName(path)

    def getName(self, path):
        """
        Retourne l'intitulé complet de la déclaration dans un format lisible
        """
        return f'{self.getType(path)} n° {self.getNumero(path)} du {self.getDate(path)}'

    def getType(self, path):
        """
        Retourne le type de déclaration
        """

        declarationCodes = {'DT': 'DT', 'DICT': 'DICT',
                            'DDC': 'DT-DICT conjointe', 'ATU': 'ATU'}

        fileName = path.stem
        return declarationCodes[fileName.split('_')[1]]

    def getNumero(self, path):
        """
        Retourne le numéro de la déclaration
        """
        fileName = path.stem
        return fileName.split('_')[0][8:].lstrip('0')

    def getDate(self, path):
        """
        Retourne la date de la déclaration
        """
        fileName = path.stem
        dayOfMonth = fileName[6:8].lstrip('0')
        month = calendar.month_name[int(fileName[4:6])]
        year = fileName[0:4]
        day = calendar.day_name[calendar.weekday(int(year), int(fileName[4:6]), int(dayOfMonth))]

        return f'{day} {dayOfMonth} {month} {year}'