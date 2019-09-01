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
""" The Translation Project system connector. """

import smtplib
from email.message import EmailMessage

from lxml import html
import requests

import datetime
from dateutil.tz import tzlocal
import polib
import re
import os
import shutil
from pathlib import Path

from ..formats.entry import POEntry
from ..formats.gettext import GettextFormat
from .systemException import ProjectNotFoundSystemException

class TPProject:
    def __init__(self, conf, name, lang, data = {}):
        self.uri = "https://translationproject.org"
        self.conf = conf
        self.name = name
        self.lang = lang
        self.basedir = ''
        self.data = data
        if "version" in data:
            self.version = data['version']

    def open(self, basedir):
        self.basedir = basedir
        self.updateFileName()
        self.updateGettextNames()

    def initialize(self, basedir, callback=None):
        self.basedir = basedir
        self.updateVersion()
        self.updateFileName()
        self.updateGettextNames()
        self.getpot()
        self.getpo()

    def getpo(self):
        pofile = requests.get('https://translationproject.org/PO-files/' + self.lang + '/' + self.filename)
        if(pofile.status_code == 200):
            with open(self.popath, 'wb') as f:
                f.write(pofile.text.encode('utf-8'))
        else:
            shutil.copy(self.potpath, self.popath)

    def getpot(self):
        with open(self.potpath, 'wb') as f:
            potfile = requests.get('http://translationproject.org/POT-files/'
                    + self.name + '-' + self.version + '.pot')
            f.write(potfile.text.encode('utf-8'))

    def updateGettextNames(self):
        self.popath = self.basedir + '/' + self.filename
        self.potpath = self.basedir + '/orig.pot'

    def updateVersion(self):
        url = 'https://translationproject.org/domain/' + self.name + '.html'
        page = requests.get(url)
        if int(page.status_code) >= 400:
            raise ProjectNotFoundSystemException(self.name)
        tree = html.fromstring(page.content)
        pot = tree.xpath('//a[contains(@href,"POT-file")]/text()')
        self.version = re.sub(self.name+'-(.*).pot$', '\\1', str(pot[0]))
        self.data['version'] = self.version

    def updateFileName(self):
        self.filename = self.name + '-' + self.version + '.' + self.lang + '.po'

    def update(self, callback):
        oldversion = self.version
        oldname = self.filename
        oldpath = self.popath
        self.updateVersion()
        self.updateFileName()
        self.updateGettextNames()
        newname = self.popath
        self.popath = self.popath + '.new.po'
        self.getpot()
        self.getpo()
        newcontent = GettextFormat(
                {'file': self.popath,
                 'pot': self.potpath,
                 'version': '0.1',
                 'fullname': self.conf['fullname'],
                 'lang': self.lang})
        content = GettextFormat(
                {'file': oldpath,
                 'pot': self.potpath,
                 'version': '0.1',
                 'fullname': self.conf['fullname'],
                 'lang': self.lang})
        newcontent.merge(content, callback)
        self.po = newcontent
        os.remove(oldpath)
        os.rename(self.popath, newname)
        self.popath = newname

    def send(self, interface):
        self.save()
        msg = EmailMessage()
        msg['Subject'] = self.filename
        msg['From'] = self.conf["email"]
        msg['To'] = 'robot@translationproject.org'
        with open(self.popath, 'rb') as f:
            msg.add_attachment(f.read(), maintype='text', subtype='plain',
                        filename=self.filename)
        with smtplib.SMTP(self.conf['server']+':587') as s:
            s.starttls()
            s.login(self.conf['user'], interface.askPassword())
            s.send_message(msg)

    def save(self):
        self.po.save()

    def content(self):
        self.po = GettextFormat(
                {'file': self.popath,
                 'pot': self.potpath,
                 'version': '0.1',
                 'fullname': self.conf['fullname'],
                 'lang': self.lang})
        return {'default': self.po.content()}

    @staticmethod
    def isConfigured(conf):
        res = 'email' in conf and conf['email'] != '' and conf['email'] != None
        res = res and 'fullname' in conf and conf['fullname'] != '' and \
                conf['fullname'] != None
        res = res and 'server' in conf and conf['server'] != '' and \
                conf['server'] != None
        res = res and 'user' in conf and conf['user'] != '' and \
                conf['user'] != None
        return res
