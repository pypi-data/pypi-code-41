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

class Entry:
    def __init__(self, msgids, msgstrs, fuzzy, obsolete):
        self.msgids = msgids
        self.msgstrs = msgstrs
        self.fuzzy = fuzzy
        self.obsolete = obsolete

    def isTranslated(self):
        for msgstr in self.msgstrs:
            if msgstr == '':
                return False
        return True

    def isFuzzy(self):
        return self.fuzzy

    def isObsolete(self):
        return self.obsolete

    def update(self, index, content):
        self.msgstrs[index] = content

    def get(self, index):
        return self.msgstrs[index]

class POEntry(Entry):
    def __init__(self, entry):
        msgids = [entry.msgid]
        msgstrs = [entry.msgstr]
        if 0 in entry.msgstr_plural:
            msgstrs = []
            for msgstr in entry.msgstr_plural:
                msgstrs.append(entry.msgstr_plural[msgstr])
            msgids = [entry.msgid, entry.msgid_plural]
        Entry.__init__(self, msgids, msgstrs, "fuzzy" in entry.flags, entry.obsolete)
        self.entry = entry

    def update(self, index, content):
        Entry.update(self, index, content)
        self.fuzzy = False
        self.entry.flags = [x for x in self.entry.flags if x != 'fuzzy']
        if 0 in self.entry.msgstr_plural:
            self.entry.msgstr_plural[index] = content
        else:
            self.entry.msgstr = content

class JSONEntry(Entry):
    def __init__(self, entry):
        Entry.__init__(self, [entry['source_string']], [entry['translation']], False, False)
        self.entry = entry

    def update(self, index, content):
        Entry.update(self, index, content)
        self.entry['translation'] = content

class YAMLEntry(Entry):
    def __init__(self, entry):
        self.entry = entry
        Entry.__init__(self, [entry['source_string']],
                [entry['translation']], False, False)

    def update(self, index, content):
        Entry.update(self, index, content)
        self.entry['translation'] = content

class TSEntry(Entry):
    def __init__(self, entry):
        self.entry = entry
        numerus = entry.get('numerus') == 'yes'
        sourcestring = ""
        translation = [] if numerus else ""
        translationtype = None
        for child in entry:
            if child.tag == "source":
                sourcestring = child.text
            elif child.tag == "translation":
                translationtype = child.get('type')
                if numerus:
                    for form in child:
                        txt = form.text
                        translation.append("" if txt is None else txt)
                else:
                    txt = child.text
                    translation = "" if txt is None else txt
        if numerus:
            sourcestring = [sourcestring, sourcestring]
        else:
            translation = [translation]
            sourcestring = [sourcestring]
        fuzzy = False
        obsolete = False
        if translationtype == 'obsolete':
            obsolete = True
        if translationtype == 'unfinished':
            fuzzy = True
        Entry.__init__(self, sourcestring, translation, fuzzy, obsolete)

    def update(self, index, content):
        Entry.update(self, index, content)
        numerus = self.entry.get('numerus') == 'yes'
        for child in self.entry:
            if child.tag == "translation":
                if numerus:
                    i=0
                    self.fuzzy = False
                    for form in child:
                        if i == index:
                            form.text = content
                        if form.text == '':
                            self.fuzzy = True
                        i = i + 1
                else:
                    child.text = content
                    self.fuzzy = content == ""
