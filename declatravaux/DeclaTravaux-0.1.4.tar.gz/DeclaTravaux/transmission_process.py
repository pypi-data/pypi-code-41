#!/usr/bin/env python

from PyPDF2.pdf import PdfFileReader

from pathlib import Path, PurePath
from zipfile import ZipFile, BadZipfile
from xml.etree import ElementTree

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate

import re
import smtplib
import socket

from DeclaTravaux.configuration import Configuration

class TransmissionProcess():

    def __init__(self, declaration):
        self.cfg = Configuration()
        self.declaration = declaration
        self.declarationPath = Path(self.cfg['RepertoireDeclarations'], PurePath(self.declaration.fileName).stem)
        self.archiveDest = PurePath(
                            self.cfg['RepertoireDeclarations'],
                            'Archives',
                            f'{PurePath(self.declaration.fileName).stem}-d{PurePath(self.declaration.fileName).suffix}',
                            )

    def __iter__(self):

        try:
            yield 'Extraction de l’archive'
            self.extractArchive()

            yield 'Identification des destinataires'
            self.operators = self.getOperators()

            yield 'Connexion au serveur SMTP'
            self.connexion = self.getConnexion()

            yield 'Envoi des courriels'
            self.sentEmails, self.noDemat, self.noPdf = self.sendEmails()

            yield 'Envoi du courriel récapitulatif'
            self.sendRecapEmail()

            yield 'Terminé'

        except BadZipfile:
            self.undoProcess()
            yield ('ZipFileError', 'L’archive ne contient pas les données attendues ou est corrompue.')

        except socket.gaierror:
            self.undoProcess()
            yield ('ConnectionError', 'Veuillez vérifier votre connexion Internet.')

        except smtplib.SMTPAuthenticationError:
            self.undoProcess()
            yield ('AuthentificationError', 'Veuillez vérifier votre adresse électronique et votre mot de passe.')

    def extractArchive(self):
        """
        Extrait l'archive obtenue après l'utilisation du téléservice dans le répertoire indiqué en paramètre.
        Retourne le chemin vers le dossier où l'archive a été extraite.
        """

        # Création d'un répertoire qui contiendra le contenu extrait de l'archive ;
        # ce répertoire a pour nom le numéro de la déclaration.
        destination = PurePath(self.cfg['RepertoireDeclarations'], PurePath(self.declaration.fileName).stem)
        Path(destination).mkdir(parents=True)

        # On extrait l'ensemble du contenu de l'archive
        # dans le répertoire venant d'être créé.
        archive = ZipFile(self.declaration.filePath)
        archive.extractall(destination)
        archive.close()

        # L'archive principale contient elle-même une archive
        # On extrait donc cette sous-archive et on supprime le fichier .zip correspondant

        subArchivePath = PurePath(destination, PurePath(self.declaration.fileName).stem + '_description.zip')

        subArchive = ZipFile(subArchivePath)
        subArchive.extractall(destination)
        subArchive.close()
        Path(subArchivePath).unlink()

        # L'archive est déplacée dans le dossier « Archives » du répertoire des déclarations
        if not Path(self.cfg['RepertoireDeclarations'], 'Archives').exists():
            Path(self.cfg['RepertoireDeclarations'], 'Archives').mkdir()

        Path(self.declaration.filePath).rename(self.archiveDest)

        return True

    def getOperators(self):
        """
        Retourne la liste des destinataires définis dans le fichier ***_description.xml,
        dont le chemin est indiqué en paramètre
        """

        # On récupère le dictionnaire associant le nom de l'exploitant et son fichier PDF
        pdfList = self.associatePdf()

        # On reconstitue le chemin du fichier « *_description.xml »
        xmlFilePath = Path(self.declarationPath, PurePath(self.declaration.fileName).stem + '_description.xml')

        # On parse le fichier XML et on se place à la racine
        xmlFile = ElementTree.parse(xmlFilePath)
        root = xmlFile.getroot()

        # On indique le namespace utilisé dans le fichier XML
        ns = {'t': 'http://www.reseaux-et-canalisations.gouv.fr/schema-teleservice/3.0',
                'ie': 'http://xml.insee.fr/schema'}

        # On crée la liste des destinataires, qui contient l'ensemble des destinataires
        # indiqués dans le fichier XML sous la forme de dictionnaires,
        # qui contiennent un certain nombre d'informations.
        operators = list()

        # On alimente la liste des destinataires.
        for tag in root.findall('t:listeDesOuvrages/t:ouvrage', ns):

            ouvrage = tag.findtext('t:classeOuvrage', '', ns).replace('_', ' ')
            
            lastName = tag.findtext('t:listeDesZones/t:zone/t:contact/t:nom/ie:NomFamille', '', ns)
            firstName = tag.findtext('t:listeDesZones/t:zone/t:contact/t:prenom/ie:Prenom', '', ns)
            company = tag.findtext('t:listeDesZones/t:zone/t:contact/t:societe', '', ns)
            agency = tag.findtext('t:listeDesZones/t:zone/t:contact/t:agence', '', ns)
            complement = tag.findtext('t:listeDesZones/t:zone/t:contact/t:complement', '', ns)
            numero = tag.findtext('t:listeDesZones/t:zone/t:contact/t:numero', '', ns)
            street = tag.findtext('t:listeDesZones/t:zone/t:contact/t:voie', '', ns)
            postbox = tag.findtext('t:listeDesZones/t:zone/t:contact/t:lieuDitBP', '', ns)
            postcode = tag.findtext('t:listeDesZones/t:zone/t:contact/t:codePostal', '', ns)
            locality = tag.findtext('t:listeDesZones/t:zone/t:contact/t:commune', '', ns)
            countryCode = tag.findtext('t:listeDesZones/t:zone/t:contact/t:codePays', '', ns)
            email = tag.findtext('t:listeDesZones/t:zone/t:contact/t:mailObligatoire/t:courriel', '', ns)
            phoneNumber = tag.findtext('t:listeDesZones/t:zone/t:contact/t:telephone', '', ns)
            faxNumber = tag.findtext('t:listeDesZones/t:zone/t:contact/t:fax', '', ns)
            emergencyEmail = tag.findtext('t:listeDesZones/t:zone/t:contact/t:mailUrgence', '', ns)
            emergencyPhoneNumber = tag.findtext('t:listeDesZones/t:zone/t:contact/t:telephoneUrgence', '', ns)
            emergencyFaxNumber  = tag.findtext('t:listeDesZones/t:zone/t:contact/t:faxUrgence', '', ns)
            dommagePhoneNumber = tag.findtext('t:listeDesZones/t:zone/t:contact/t:telEndommagement', '', ns)
            dematManagement = tag.findtext('t:listeDesZones/t:zone/t:contact/t:gestionDesFichiersDematerialises/t:gereLesFichiersDematerialises', '', ns)
            dematManagement = True if dematManagement == 'true' else False
            dematFileFormat = tag.findtext('t:listeDesZones/t:zone/t:contact/t:gestionDesFichiersDematerialises/t:formatDesFichiersDematerialises', '', ns)

            # On associe le destinataire au fichier PDF qui lui correspond.
            pdfFile = [f for f, oDict in pdfList.items() if oDict['Name'] == company and (
                                                                    oDict['Destinator'] == company or
                                                                    oDict['Destinator'] == ' '.join((agency, lastName)).strip()
                                                                    )]
            
            # pdfFile reprend le nom du pdf associé
            # ou se voit affecté de la valeur « False » si aucun PDF n'est trouvé
            if pdfFile:
                pdfFile = pdfFile[0]
            else:
                pdfFile = False

            # On ajoute un dictionnaire à la liste avec l'ensemble des informations récupérées.
            operators.append({'ouvrage':ouvrage, 'company':company, 'agency':agency,
                                'numero':numero, 'street':street, 'postcode':postcode,
                                'locality':locality, 'countryCode':countryCode,
                                'email':email, 'phoneNumber':phoneNumber, 'faxNumber':faxNumber,
                                'emergencyEmail':emergencyEmail,
                                'emergencyPhoneNumber':emergencyPhoneNumber,
                                'emergencyFaxNumber':emergencyFaxNumber,
                                'dommagePhoneNumber':dommagePhoneNumber,
                                'dematManagement':dematManagement,
                                'dematFileFormat':dematFileFormat,
                                'pdfFile':pdfFile
                                        })

        return operators

    def associatePdf(self):
        """
        Retourne un dictionnaire associant le nom des fichiers PDF
        au nom des exploitants concernés.

        La fonction est relativement lourde dès lors qu'elle s'appuie sur la bibliothèque PyPDF2.
        """

        pdfFileRegex = re.compile(r'[0-9]{13}[A-Z]{1}([0-9][0-9])?_(.)*_[0-9]{1,2}.pdf')
        # La liste est filtrée pour ne conserver que les formulaires PDF
        filesList = [str(f.resolve()) for f in self.declarationPath.iterdir() if pdfFileRegex.match(f.name)]
        # La liste est triée par ordre croissant
        filesList.sort()

        # Un dictionnaire est créé sous la avec la structure suivante :
        # - clé = nom du fichier PDF ;
        # - valeur = nom de l'exploitant.

        pdfDict = dict()

        for f in filesList:
            field = PdfFileReader(f).getFields()
            pdfDict[f] = dict()
            pdfDict[f]['Name'] = field['Exploitant']['/V'].strip()
            pdfDict[f]['Destinator'] = field['Destinataire']['/V'].strip()

        return pdfDict

    def getConnexion(self):
        """
        Renvoie une connexion au serveur SMTP
        """
        connexion = smtplib.SMTP_SSL(self.cfg['ServeurSMTP'], self.cfg['PortServeurSMTP'])
        connexion.login(self.cfg['AdresseElectronique'], self.cfg.password)

        return connexion

    def sendEmails(self):
        """
        Envoi par courriel des fichiers nécessaires aux différents destinataires identifiés.

        Les fichiers envoyés par courriel dépendent du niveau de dématérialisation du destinataire :
        - pas de dématérialisation : aucun courriel n'est envoyé ;
        - dématérialisation XML et PDF : envoi des fichiers « *_description.xml », « *_emprise.pdf » et « *_ZZZZ_*.pdf » ;
        - dématérialisation XML : envoi du fichier « *_description.xml ».
        """

        sentEmails = list()
        noPdf = list()
        noDemat = list()

        for operator in self.operators:

            # Un courriel n'est envoyé que si le destinataire gère les fichiers dématérialisés
            if not operator['pdfFile']:
                
                noPdf.append({'ouvrage':operator['ouvrage'],
                                'company':operator['company'],
                                'dematManagement': operator['dematManagement'],
                                'dematFileFormat':operator['dematFileFormat'],
                                'email':operator['email'],
                                'files':[],
                                })

            elif not operator['dematManagement']:
                
                noDemat.append({'ouvrage':operator['ouvrage'],
                                'company':operator['company'],
                                'dematManagement': operator['dematManagement'],
                                'dematFileFormat':operator['dematFileFormat'],
                                'email':operator['email'],
                                'files':[operator['pdfFile'],
                                            self.cfg['RepertoireDeclarations'] + '/' + PurePath(self.declaration.fileName).stem + '/'
                                            + PurePath(self.declaration.fileName).stem + '_emprise.pdf',],
                                })
            
            elif operator['dematManagement']:

                # Le courriel envoyé contient un message, à la fois en version HTML et version texte, ainsi que des pièces jointes.
                #
                # Un tel courriel doit avoir la structure suivante :
                #   - Courriel (multipart/mixed)
                #       - Message (multipart/alternative)
                #           - Version texte du message (text/plain)
                #           - Version HTML du message (text/html)
                #       - Pièce jointe n° 1 (application/***)
                #       - ...
                #       - Pièce jointe n° n (application/***)


                # CRÉATION DE L'EN-TÊTE DU COURRIEL

                email = MIMEMultipart('mixed')

                email['From'] = self.cfg['AdresseElectronique']
                email['To'] = operator['email']
                email['Subject'] = 'Notification d’une déclaration de travaux'
                email['Date'] = formatdate(localtime=True)
                email['Charset'] = 'UTF-8'

                # CRÉATION DU MESSAGE (VERSION TEXTE ET VERSION HTML)

                messagePart = MIMEMultipart('alternative')


                textSubpart = """
                                Madame, Monsieur,\n
                                Veuillez trouver ci-joint les éléments
                                relatifs à une déclaration de travaux.\n
                                Meilleures salutations,\n
                                """ + self.cfg['NomExpediteur']

                htmlSubpart = """
                                <html>
                                    <head></head>
                                    <body>
                                        <p>Madame, Monsieur,</p>
                                        <p>
                                            Veuillez trouver ci-joint les éléments
                                            relatifs à une déclaration de travaux.
                                        </p>
                                        <p>Meilleures salutations,</p>
                                        <p>""" + self.cfg['NomExpediteur'] + """</p>
                                    </body>
                                </html>
                                """

                # Attribution du type MIME correspondant à chaque version
                textSubpart = MIMEText(textSubpart, 'plain')
                htmlSubpart = MIMEText(htmlSubpart, 'html')

                # Leux deux versions sont intégrées au conteneur « messagePart »
                messagePart.attach(textSubpart)
                messagePart.attach(htmlSubpart)

                # Le conteneur « messagePart » est lui-même intégré au conteneur principal « email »
                email.attach(messagePart)


                # AJOUT DES PIÈCES JOINTES

                # Les pièces jointes sont listées dans la variable « attachments »

                # Quelque soit le niveau de dématérialisation, le fichier *_description.xml est envoyé
                attachments = [self.cfg['RepertoireDeclarations'] + '/' + PurePath(self.declaration.fileName).stem + '/'
                                + PurePath(self.declaration.fileName).stem + '_description.xml',]

                # Si la dématérialisation est de type XML / PDF, il faut ajouter les fichiers *_emprise.pdf et *_ZZZZ_*.pdf
                if operator['dematFileFormat'] == 'XML_PDF':
                    # Fichier *_emprise.pdf
                    attachments.append(self.cfg['RepertoireDeclarations'] + '/' + PurePath(self.declaration.fileName).stem + '/'
                                + PurePath(self.declaration.fileName).stem + '_emprise.pdf')
                    # Fichier *_ZZZZ_*.pdf
                    attachments.append(operator['pdfFile'])

                # Chaque fichier contenu dans la variable « attachments »
                # est intégré au conteneur principal « mail » en tant que pièce jointe.
                for f in attachments:

                    attachment = open(f, 'rb')

                    attachmentPart = MIMEBase('application', 'octet-stream')
                    attachmentPart.set_payload((attachment).read())
                    encoders.encode_base64(attachmentPart)
                    attachmentPart.add_header('Content-Disposition', f'attachment; filename="{Path(f).name}"')

                    email.attach(attachmentPart)

                # Envoi du courriel
                email = email.as_string()
                self.connexion.sendmail(self.cfg['AdresseElectronique'], operator['email'], email)

                # Liste récapitulative des courriels envoyés
                sentEmails.append({'ouvrage':operator['ouvrage'],
                                'company':operator['company'],
                                'dematManagement': operator['dematManagement'],
                                'dematFileFormat':operator['dematFileFormat'],
                                'email':operator['email'],
                                'files':attachments
                                })

        return (sentEmails, noDemat, noPdf)

    def sendRecapEmail(self):
        """
        Envoie un courriel récapitulatif à l'adresse électronique de l'expéditeur.
        """

        # Le courriel envoyé contient un message, à la fois en version HTML et version texte.
        # Il n'y a pas de pièce jointe.
        #
        # Un tel courriel doit avoir la structure suivante :
        #   - Courriel (multipart/alternative)
        #       - Version texte du message (text/plain)
        #       - Version HTML du message (text/html)
        
        # CRÉATION DE L'EN-TÊTE DU COURRIEL

        email = MIMEMultipart('alternative')

        email['From'] = self.cfg['AdresseElectronique']
        email['To'] = self.cfg['AdresseElectronique']
        email['Subject'] = 'Récapitulatif de la transmission électronique de la déclaration de travaux'
        email['Date'] = formatdate(localtime=True)
        email['Charset'] = 'UTF-8'

        # CRÉATION DU MESSAGE (VERSION TEXTE ET VERSION HTML)
        
        # Tableau des fichiers envoyés
        textTableSent = ''
        htmlTableSent = ''
        htmlTableSent += '<table style="border-collapse: separate; border-spacing: 0px 5px; margin: auto; font-size: small;">'
        htmlTableSent += '<tr><th>Destinataire</th><th>Courriel</th><th>Fichiers envoyés</th></tr>'

        for entry in self.sentEmails:
            textTableSent += f'| {entry["company"]} | {entry["email"]} | '
            htmlTableSent += f'<tr><td style="border-top: 1px solid black; border-bottom: 1px solid black; padding: 4px 8px;">'
            htmlTableSent += f'<class style="font-weight: bold">{entry["company"]}</class><br />'
            htmlTableSent += f'{entry["ouvrage"]}</td>'
            htmlTableSent += f'<td style="border-top: 1px solid black; border-bottom: 1px solid black; padding: 4px 8px;">'
            htmlTableSent += f'{entry["email"]}</td>'
            htmlTableSent += f'<td style="border-top: 1px solid black; border-bottom: 1px solid black; padding: 4px 8px;">'

            for f in entry['files']:
                textTableSent += f'{Path(f).name} '
                htmlTableSent += f'{Path(f).name}<br />'

            textTableSent += ' |\n'
            htmlTableSent += '</td></tr>'

        htmlTableSent += '</table>'
        
        #Tableau des fichiers non envoyés
        textTableUnsent = ''
        htmlTableUnsent = ''
        htmlTableUnsent += '<table style="border-collapse: separate; border-spacing: 0px 5px; margin: auto; font-size: small;">'
        htmlTableUnsent += '<tr><th>Destinataire</th><th>Motif</th><th>Courriel</th><th>Fichiers à envoyer</th></tr>'
        
        unsentEmails = self.noDemat + self.noPdf
        
        for entry in unsentEmails:
            textTableUnsent += f'| {entry["company"]} | {entry["email"]} | '
            htmlTableUnsent += f'<tr><td style="border-top: 1px solid black; border-bottom: 1px solid black; padding: 4px 8px;">'
            htmlTableUnsent += f'<class style="font-weight: bold">{entry["company"]}</class><br />'
            htmlTableUnsent += f'{entry["ouvrage"]}</td>'
            htmlTableUnsent += f'<td style="border-top: 1px solid black; border-bottom: 1px solid black; padding: 4px 8px;">'
            
            if not entry['files']:
                htmlTableUnsent += 'Aucun fichier PDF trouvé</td>'
            elif not entry['dematManagement']:
                htmlTableUnsent += 'À envoyer au format papier</td>'
            
            htmlTableUnsent += f'<td style="border-top: 1px solid black; border-bottom: 1px solid black; padding: 4px 8px;">'
            htmlTableUnsent += f'{entry["email"]}</td>'
            htmlTableUnsent += f'<td style="border-top: 1px solid black; border-bottom: 1px solid black; padding: 4px 8px;">'

            for f in entry['files']:
                textTableUnsent += f'{Path(f).name} '
                htmlTableUnsent += f'{Path(f).name}<br />'

            textTableUnsent += ' |\n'
            htmlTableUnsent += '</td></tr>'

        htmlTableUnsent += '</table>'
        
        # Assemblage des tableaux
        textPart = ''
        textPart += 'Voici le récapitulatif de transmission de la déclaration :\n\n'
        textPart += self.declaration.name + '\n\n'
        textPart += textTableUnsent


        htmlPart = f'''
                    <html>
                        <head></head>
                        <body>
                            <p>Voici le récapitulatif de transmission de la déclaration :</p>
                            <p style="text-align: center; font-weight: bold;">
                                {self.declaration.name}
                            </p>
                            {htmlTableSent}
                            '''
        
        if unsentEmails:
            htmlPart += f'''<p style="text-align: center;">Attention : les fichiers suivants n'ont pas pu être transmis :</p>
                            {htmlTableUnsent}
                        '''
        
        htmlPart += f'''
                        </body>
                    </html>
                    '''

        # Attribution du type MIME correspondant à chaque version
        textPart = MIMEText(textPart, 'plain')
        htmlPart = MIMEText(htmlPart, 'html')

        # Leux deux versions sont intégrées au courriel
        email.attach(textPart)
        email.attach(htmlPart)

        # Envoi du courriel
        email = email.as_string()
        self.connexion.sendmail(self.cfg['AdresseElectronique'], self.cfg['AdresseElectronique'], email)
    
    def undoProcess(self):
        """
        Annule les déplacements de fichiers réalisés
        """

        # Le cas échéant, l'archive est rétablie dans son dossier initial
        if Path(self.archiveDest).exists():
            Path(self.archiveDest).rename(self.declaration.filePath)

        # Le cas échéant, le dossier de travail correspondant à la déclaration en cours est vidé puis supprimé
        if Path(self.declarationPath).exists():
            for f in Path(self.declarationPath).iterdir():
                Path(f).unlink()

            Path(self.declarationPath).rmdir()