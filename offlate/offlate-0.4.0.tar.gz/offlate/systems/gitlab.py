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
""" The gitlab system connector. """

from .git import GitProject

from urllib.parse import urlparse
import gitlab

class GitlabProject(GitProject):
    def __init__(self, conf, name, lang, data = {}):
        GitProject.__init__(self, conf, name, lang, data)

    def updateURI(self):
        self.uri = self.data['repo']
        self.branch = self.data['branch']

    def send(self, interface):
        server = urlparse(self.uri).hostname
        token = ""
        for serv in self.conf["servers"]:
            if serv["server"] == server:
                token = serv["token"]
                break

        if token == "":
            interface.gitlabTokenNotFound(server)
            return

        gl = gitlab.Gitlab("https://"+server, private_token=token)
        gl.auth()

        currentUser = gl.user.username
        projectname = self.uri.split('/')[-1]
        projectfullname = urlparse(self.uri).path[1:]

        originproject = gl.projects.get(projectfullname)
        try:
            project = gl.projects.get(currentUser + "/" + projectname)
        except:
            project = project.forks.create({})

        try:
            branch = project.branches.create({'branch': 'translation', 'ref': self.branch})
        except:
            interface.gitlabTokenBranchError('translation')
            return
        actions = []
        for mfile in self.translationfiles:
            mfile = mfile['filename']
            try:
                project.files.get(file_path=mfile, ref=self.branch)
                actions.append({'action': 'update',
                    'file_path': mfile,
                    'content': open(self.basedir + '/current/' + mfile).read()})
            except:
                actions.append({'action': 'create',
                    'file_path': mfile,
                    'content': open(self.basedir + '/current/' + mfile).read()})
        if actions == []:
            return
        project.commits.create({
            'branch': 'translation',
            'commit_message': 'Update \'' + self.lang + '\' translation',
            'actions': actions
            })
        project.mergerequests.create({'source_branch': 'translation',
            'target_branch': self.branch, 'target_project_id': originproject.id,
            'title': 'Update \'' + self.lang + '\' translation'})

    @staticmethod
    def isConfigured(conf):
        res = GitProject.isConfigured(conf)
        res = res and 'servers' in conf and conf['servers'] != '' and \
                conf['servers'] != None
        return res
