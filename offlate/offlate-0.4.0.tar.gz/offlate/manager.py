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

from pathlib import Path
from .systems.tp import TPProject
from .systems.transifex import TransifexProject
from .systems.gitlab import GitlabProject
from .formats.formatException import UnsupportedFormatException
from .systems.list import *

import json
import os

def rmdir(dir):
    dir = Path(dir)
    for item in dir.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    dir.rmdir()

class ProjectSettings:
    def __init__(self, confdir):
        self.confdir = confdir
        self.reload()

    def write(self):
        with open(self.confdir + '/conf.json', 'w') as f:
            f.write(json.dumps(self.conf))

    def reload(self):
        try:
            with open(self.confdir + '/conf.json') as f:
                self.conf = json.load(f)
        except Exception:
            with open(self.confdir + '/conf.json', 'w') as f:
                f.write(json.dumps({}))

class ProjectManager:
    def __init__(self):
        self.projects = []
        self.project_list = dict()
        home = str(Path.home())
        self.basedir = home + '/.local/share/offlate'
        self.confdir = home + '/.config/offlate'
        Path(self.basedir).mkdir(parents=True, exist_ok=True)
        Path(self.confdir).mkdir(parents=True, exist_ok=True)
        self.settings = ProjectSettings(self.confdir)
        try:
            with open(self.basedir + '/projects.json') as f:
                self.projects = json.load(f)
                for p in self.projects:
                    proj = self.loadProject(p['name'], p['lang'], p['system'],
                            p['info'])
                    proj.open(self.basedir+'/'+p['name'])
        except Exception as e:
            print(e)
            with open(self.basedir + '/projects.json', 'w') as f:
                f.write(json.dumps([]))

    def createProject(self, name, lang, system, data, callback):
        callback.progress(0)

        projectpath = self.basedir + '/' + name
        path = Path(projectpath)
        if not path.exists():
            path.mkdir(parents=True)
        else:
            if len([x for x in self.projects if x['name'] == name]) > 0:
                callback.project_exists()
            else:
                callback.project_present(projectpath)
            return False

        try:
            data["version"] = "0.3"
            proj = self.loadProject(name, lang, system, data)
            proj.initialize(projectpath, callback)
            self.projects.append({"name": name, "lang": lang, "system": system,
                "info": data})
        except Exception as e:
            callback.project_error(e)
            rmdir(projectpath)
            return False

        callback.progress(100)

        self.writeProjects()
        return True

    def loadProject(self, name, lang, system, data):
        if not "Generic" in self.settings.conf:
            self.settings.conf["Generic"] = {}
        if system == TRANSLATION_PROJECT:
            if not "TP" in self.settings.conf:
                self.settings.conf["TP"] = {}
            settings = self.settings.conf["TP"]
            for s in self.settings.conf["Generic"].keys():
                settings[s] = self.settings.conf["Generic"][s]
            proj = TPProject(settings, name, lang, data)
        if system == TRANSIFEX:
            if not 'Transifex' in self.settings.conf:
                self.settings.conf['Transifex'] = {}
            settings = self.settings.conf["Transifex"]
            for s in self.settings.conf["Generic"].keys():
                settings[s] = self.settings.conf["Generic"][s]
            proj = TransifexProject(settings, name, lang, data)
        if system == GITLAB:
            if not 'Gitlab' in self.settings.conf:
                self.settings.conf['Gitlab'] = {}
            settings = self.settings.conf["Gitlab"]
            for s in self.settings.conf["Generic"].keys():
                settings[s] = self.settings.conf["Generic"][s]
            proj = GitlabProject(settings, name, lang, data)
        self.project_list[name] = proj
        return proj

    def update(self):
        for p in self.projects:
            proj = self.project_list[p['name']]
            p['info'] = proj.data

    def writeProjects(self):
        with open(self.basedir + '/projects.json', 'w') as f:
            f.write(json.dumps(self.projects))

    def listProjects(self):
        return self.projects

    def getProject(self, name):
        return self.project_list[name]

    def updateSettings(self, data=None):
        if data == None:
            self.settings.conf = data
            self.settings.update()
        else:
            self.settings.write()

    def getConf(self):
        return self.settings.conf

    def remove(self, name):
        rmdir(self.basedir + '/' + name)
        self.projects = [x for x in self.projects if x['name'] != name]
        self.writeProjects()

    def updateProject(self, name, lang, system, info, callback):
        try:
            rmdir(self.basedir + '/' + name)
        except:
            pass
        self.projects = [x for x in self.projects if x['name'] != name]
        return self.createProject(name, lang, system, info, callback)

    def isConfigured(self, system):
        if system == TRANSLATION_PROJECT:
            if not "TP" in self.settings.conf:
                self.settings.conf["TP"] = {}
            settings = self.settings.conf["TP"]
            for s in self.settings.conf["Generic"].keys():
                settings[s] = self.settings.conf["Generic"][s]
            return TPProject.isConfigured(settings)
        elif system == TRANSIFEX:
            if not "Transifex" in self.settings.conf:
                self.settings.conf["Transifex"] = {}
            settings = self.settings.conf["Transifex"]
            for s in self.settings.conf["Generic"].keys():
                settings[s] = self.settings.conf["Generic"][s]
            return TransifexProject.isConfigured(settings)
        elif system == GITLAB:
            if not "Gitlab" in self.settings.conf:
                self.settings.conf["Gitlab"] = {}
            settings = self.settings.conf["Gitlab"]
            for s in self.settings.conf["Generic"].keys():
                settings[s] = self.settings.conf["Generic"][s]
            return GitlabProject.isConfigured(settings)
        else:
            return False
