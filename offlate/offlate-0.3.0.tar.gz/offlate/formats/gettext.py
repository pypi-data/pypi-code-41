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
""" The gettext format. """

import polib
import datetime
import os.path
from dateutil.tz import tzlocal
from .entry import POEntry

class GettextFormat:
    def __init__(self, conf):
        self.pofilename = conf["file"]
        if os.path.isfile(conf["file"]):
            self.po = polib.pofile(conf["file"])
        else:
            self.po = polib.pofile(conf["pot"])
        self.pot = polib.pofile(conf["pot"])
        self.conf = conf

    def content(self):
        po = [POEntry(x) for x in self.po]
        return po

    def save(self):
        self.po.metadata['PO-Revision-Date'] = str(datetime.datetime.now(tzlocal()).__format__("%Y-%m-%d %H:%M%z"))
        self.po.metadata['Last-Translator'] = self.conf['fullname']
        self.po.metadata['Language'] = self.conf['lang']
        self.po.metadata['X-Generator'] = 'Offlate ' + self.conf['version']
        self.po.save(self.pofilename)

    def merge(self, older, callback):
        older.po.merge(self.pot)
        self.po.merge(self.pot)
        older.po.save()
        for oentry in older.po:
            for nentry in self.po:
                if oentry.msgid == nentry.msgid:
                    if oentry.msgstr == nentry.msgstr:
                        break
                    if oentry.msgstr == "":
                        break
                    if nentry.msgstr == "":
                        nentry.msgstr = oentry.msgstr
                        break
                    # otherwise, nentry and oentry have a different msgstr
                    nentry.msgstr = callback(nentry.msgid, oentry.msgstr, nentry.msgstr)
                    break
        self.po.save()

