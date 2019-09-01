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
""" The transifex system connector. """

import json
import os
import requests
from requests.auth import HTTPBasicAuth
from ..formats.yaml import YamlFormat
from ..formats.formatException import UnsupportedFormatException
from .systemException import ProjectNotFoundSystemException

class TransifexProject:
    def __init__(self, conf, name, lang, data={}):
        self.conf = conf
        self.name = name
        self.lang = lang
        self.basedir = ''
        self.data = data
        self.contents = {}

    def open(self, basedir):
        self.basedir = basedir
        with open(self.basedir + '/project.info') as f:
            self.files = json.load(f)
        self.slugs = [x['slug'] for x in self.files]

    def initialize(self, basedir, callback=None):
        self.basedir = basedir
        self.updateFileList()
        with open(self.basedir + '/project.info', 'w') as f:
            f.write(json.dumps(self.files))
        for slug in self.slugs:
            self.getFiles(slug)

    def updateFileList(self):
        self.files = []
        self.slugs = []
        ans = requests.get('https://api.transifex.com/organizations/'+
                self.data['organization']+'/projects/'+self.name+
                '/resources/?language_code='+self.lang,
                auth=HTTPBasicAuth('api', self.conf['token']))
        if ans.status_code == 200:
            l = json.loads(ans.text)
            self.slugs = [x['slug'] for x in l]
            self.files = l
        else:
            raise ProjectNotFoundSystemException(self.name)

    def update(self, callback):
        self.updateFileList()
        for ff in self.files:
            slug = ff['slug']
            fname = self.filename(slug, False)
            sname = self.filename(slug, True)
            os.rename(fname, fname+'.old')
            os.rename(sname, sname+'.old')
            self.getFiles(slug)
            if ff['i18n_type'] == 'YML':
                oldformat = YamlFormat({'dest': fname+'.old', 'source': sname+'.old'})
                currentformat = YamlFormat({'dest': fname, 'source': sname})
            else:
                raise UnsupportedFormatException(ff['i18n_type'])
            currentformat.merge(oldformat, callback)

    def filename(self, slug, is_source):
        ext = ''
        for ff in self.files:
            if ff['slug'] == slug:
                f = ff
                break
        if f['i18n_type'] == 'YML':
            ext = 'yml'
        else:
            raise UnsupportedFormatException(ff['i18n_type'])
        return self.basedir + '/' + slug + ('.source' if is_source else '') + '.' + ext

    def getFiles(self, slug):
        ans = requests.get('https://www.transifex.com/api/2/project/'+
                self.name+'/resource/'+slug+'/content',
                auth=HTTPBasicAuth('api', self.conf['token']))
        if ans.status_code == 200:
            with open(self.filename(slug, True), 'wb') as f:
                f.write(json.loads(ans.text)['content'].encode('utf-8'))

        ans = requests.get('https://www.transifex.com/api/2/project/'+self.name+
                '/resource/'+slug+'/translation/'+self.lang+'/?mode=translator',
                auth=HTTPBasicAuth('api', self.conf['token']))
        if ans.status_code == 200:
            with open(self.filename(slug, False), 'wb') as f:
                f.write(json.loads(ans.text)['content'].encode('utf-8'))
        else:
            print(ans.text)

    def send(self, interface):
        self.save()
        for slug in self.files:
            print('{} => {}'.format(slug['slug'], slug['i18n_type']))
            with open(self.filename(slug['slug'], False), 'rb') as f:
                content = f.read()
                sendcontent = {"content": content.decode('utf8')}
                ans = requests.put('https://www.transifex.com/api/2/project/'+
                        self.name+'/resource/'+slug['slug']+'/translation/'+self.lang+'/',
                        json=sendcontent, auth=HTTPBasicAuth('api', self.conf['token']))
                print(ans)
                print(ans.text)

    def save(self):
        for slug in self.slugs:
            slug.save()

    def content(self):
        content = {}
        self.slugs = []
        for slug in self.files:
            if slug['i18n_type'] == 'YML':
                myslug = YamlFormat(
                        {'dest':   self.filename(slug['slug'], False),
                         'source': self.filename(slug['slug'], True)})
            else:
                raise UnsupportedFormatException(ff['i18n_type'])
            self.slugs.append(myslug)
            content[slug['slug']] = myslug.content()
        return content

    @staticmethod
    def isConfigured(conf):
        return 'token' in conf and conf['token'] != '' and conf['token'] != None
