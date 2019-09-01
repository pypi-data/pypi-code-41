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
""" The git abstract system connector. """

import pygit2
from os import rename
from pathlib import Path

from translation_finder import discover
from ..formats.gettext import GettextFormat
from ..formats.ts import TSFormat
from ..formats.yaml import YamlFormat
from .systemException import ProjectNotFoundSystemException

def rmdir(dir):
    dir = Path(dir)
    for item in dir.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    dir.rmdir()

class Progress(pygit2.remote.RemoteCallbacks):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def transfer_progress(self, stats):
        if self.callback is not None:
            self.callback.progress((100.0 * stats.received_objects) / \
                    stats.total_objects)

class GitProject:
    def __init__(self, conf, name, lang, data = {}):
        self.conf = conf
        self.name = name
        self.lang = lang
        self.data = data

    def open(self, basedir):
        self.basedir = basedir
        self.updateURI()
        self.updateFiles()

    def initialize(self, basedir, callback=None):
        self.basedir = basedir
        self.updateURI()
        self.clone(basedir + "/current", callback)
        self.updateFiles()
    
    def updateURI(self):
        raise Exception("Unimplemented method in concrete class: updateURI")

    def updateFiles(self):
        self.translationfiles = self.updateFilesFromDirectory(
                self.basedir + '/current')

    def updateFilesFromDirectory(self, directory):
        translations = discover(directory)
        translationfiles = []
        path = directory + '/'
        for resource in translations:
            if resource['file_format'] == 'po':
                popath = resource['filemask'].replace('*', self.lang)
                if 'new_base' in resource:
                    potpath = resource['new_base']
                else:
                    # If there is no POT, then we can't really do anything...
                    continue
                translationfiles.append({'filename': popath,
                    'format': GettextFormat({'file': path + popath,
                        'pot': path + potpath,
                        'version': self.data['version'],
                        'fullname': self.conf['fullname'],
                        'lang': self.lang})})
            elif resource['file_format'] == 'yaml':
                yamlpath = resource['filemask'].replace('*', self.lang)
                translationfiles.append({'filename': yamlpath,
                    'format': YamlFormat({'dest': path + yamlpath,
                        'source': path + resource['template']})})
            elif resource['file_format'] == 'ts':
                yamlpath = resource['filemask'].replace('*', self.lang)
                enpath = resource['filemask'].replace('*', 'en')
                template = None
                if Path(path + enpath).exists():
                    template = enpath
                else:
                    template = Path(path).glob(resource['filemask'])[0]
                translationfiles.append({'filename': yamlpath,
                    'format': TSFormat({'file': path + yamlpath, 'lang': self.lang, 'template': template})})
            else:
                raise UnsupportedFormatException(resource['file_format'])
        return translationfiles

    def clone(self, directory, callback=None):
        try:
            pygit2.clone_repository(self.uri, directory, callbacks=Progress(callback),
                    checkout_branch=self.branch)
        except:
            raise ProjectNotFoundSystemException(self.name)

    def update(self, callback):
        rename(self.basedir + "/current", self.basedir + "/old")
        self.clone(self.basedir + "/current")
        oldfiles = self.updateFilesFromDirectory(self.basedir + "/old")
        self.updateFiles()
        newfiles = self.translationfiles
        for mfile in newfiles:
            path = mfile['filename']
            newformat = mfile['format']
            oldformat = None
            for mmfile in oldfiles:
                if mmfile['filename'] == path:
                    oldformat = mmfile['format']
            if oldformat is None:
                continue
            newformat.merge(oldformat, callback)
        rmdir(self.basedir + "/old")

    def send(self, interface):
        raise Exception("Unimplemented method in concrete class: send")

    def save(self):
        for resource in self.translationfiles:
            resource['format'].save()

    def content(self):
        content = {}
        for resource in self.translationfiles:
            print(resource['format'])
            content[resource['filename']] = resource['format'].content()
        return content

    @staticmethod
    def isConfigured(conf):
        return 'fullname' in conf and conf['fullname'] != '' and \
                conf['fullname'] != None
