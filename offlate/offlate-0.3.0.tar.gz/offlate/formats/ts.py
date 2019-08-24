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
""" The ts format for Qt applications. """

import datetime
import os.path
import xml.etree.ElementTree as ET
from .entry import TSEntry

class TSFormat:
    def __init__(self, conf):
        self.tsfilename = conf["file"]
        self.tscontent = self.parse(self.tsfilename)
        self.conf = conf
        self.savedcontent = [TSEntry(x) for x in self.tscontent]

    def parse(self, filename):
        result = []
        content = ET.parse(filename)
        root = content.getroot()
        for context in root:
            contextname = ""
            for child in context:
                if child.tag == "name":
                    contextname = child.text
                elif child.tag == "message":
                    result.append(child)
        return result

    def content(self):
        return self.savedcontent

    def save(self):
        root = ET.Element('TS')
        root.set("language", self.conf["lang"])
        tree = ET.ElementTree(root)
        content = ET.parse(self.tsfilename).getroot()
        for context in content:
            if context.tag == "context":
                for item in context:
                    if item.tag == "message":
                        numerus = item.get('numerus') == 'yes'
                        sourcestring = ""
                        for child in item:
                            if child.tag == "source":
                                sourcestring = child.text
                                break
                        msgstrs = []
                        for entry in self.savedcontent:
                            if entry.msgids[0] == sourcestring:
                                msgstrs = entry.msgstrs
                        for child in item:
                            if child.tag == "translation":
                                if numerus:
                                    i = 0
                                    for form in child:
                                        form.text = msgstrs[i]
                                        i += 1
                                else:
                                    child.text = msgstrs[0]
                                break
            root.append(context)
        with open(self.tsfilename, "w+") as f:
            f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            f.write("<!DOCTYPE TS>")
            f.write(ET.tostring(root).decode("utf-8"))

    def merge(self, older, callback):
        for entry in self.savedcontent:
            for oentry in older.savedcontent:
                if oentry.msgids[0] == entry.msgids[0]:
                    if len(oentry.msgstrs) == len(entry.msgstrs):
                        for i in range(0, len(oentry.msgstrs)):
                            if entry.msgstrs[i] == '' or \
                                    entry.msgstrs[i] == oentry.msgstrs[i]:
                                entry.update(i, oentry.msgstrs[i])
                            elif oentry.msgstrs[i] == '':
                                break
                            else:
                                entry.update(i, callback(entry.msgids[0],
                                    oentry.msgstrs[i], entry.msgstrs[i]))
                    break
        self.save()
