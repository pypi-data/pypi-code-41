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
import time
from .entry import TSEntry

from PyQt5.QtCore import *

# from https://github.com/qt/qttools/blob/5.12/src/linguist/shared/numerus.cpp
nplurals = {
  '1': [
    QLocale.Bislama,
    QLocale.Burmese,
    QLocale.Chinese,
    QLocale.Dzongkha,
    QLocale.Fijian,
    QLocale.Guarani,
    QLocale.Hungarian,
    QLocale.Indonesian,
    QLocale.Japanese,
    QLocale.Javanese,
    QLocale.Korean,
    QLocale.Malay,
    QLocale.NauruLanguage,
    QLocale.Oromo,
    QLocale.Persian,
    QLocale.Sundanese,
    QLocale.Tatar,
    QLocale.Thai,
    QLocale.Tibetan,
    QLocale.Turkish,
    QLocale.Vietnamese,
    QLocale.Yoruba,
    QLocale.Zhuang,
  ],
  '2': [
    QLocale.Abkhazian,
    QLocale.Afar,
    QLocale.Afrikaans,
    QLocale.Albanian,
    QLocale.Amharic,
    QLocale.Assamese,
    QLocale.Aymara,
    QLocale.Azerbaijani,
    QLocale.Bashkir,
    QLocale.Basque,
    QLocale.Bengali,
    QLocale.Bihari,
    QLocale.Bulgarian,
    QLocale.Catalan,
    QLocale.Cornish,
    QLocale.Corsican,
    QLocale.Danish,
    QLocale.Dutch,
    QLocale.English,
    QLocale.Esperanto,
    QLocale.Estonian,
    QLocale.Faroese,
    QLocale.Finnish,
    QLocale.Friulian,
    QLocale.WesternFrisian,
    QLocale.Galician,
    QLocale.Georgian,
    QLocale.German,
    QLocale.Greek,
    QLocale.Greenlandic,
    QLocale.Gujarati,
    QLocale.Hausa,
    QLocale.Hebrew,
    QLocale.Hindi,
    QLocale.Interlingua,
    QLocale.Interlingue,
    QLocale.Italian,
    QLocale.Kannada,
    QLocale.Kashmiri,
    QLocale.Kazakh,
    QLocale.Khmer,
    QLocale.Kinyarwanda,
    QLocale.Kirghiz,
    QLocale.Kurdish,
    QLocale.Lao,
    QLocale.Latin,
    QLocale.Lingala,
    QLocale.Luxembourgish,
    QLocale.Malagasy,
    QLocale.Malayalam,
    QLocale.Marathi,
    QLocale.Mongolian,
    QLocale.Nepali,
    QLocale.NorthernSotho,
    QLocale.NorwegianBokmal,
    QLocale.NorwegianNynorsk,
    QLocale.Occitan,
    QLocale.Oriya,
    QLocale.Pashto,
    QLocale.Portuguese,
    QLocale.Punjabi,
    QLocale.Quechua,
    QLocale.Romansh,
    QLocale.Rundi,
    QLocale.Shona,
    QLocale.Sindhi,
    QLocale.Sinhala,
    QLocale.Somali,
    QLocale.SouthernSotho,
    QLocale.Spanish,
    QLocale.Swahili,
    QLocale.Swati,
    QLocale.Swedish,
    QLocale.Tajik,
    QLocale.Tamil,
    QLocale.Telugu,
    QLocale.Tongan,
    QLocale.Tsonga,
    QLocale.Tswana,
    QLocale.Turkmen,
    QLocale.Uigur,
    QLocale.Urdu,
    QLocale.Uzbek,
    QLocale.Volapuk,
    QLocale.Wolof,
    QLocale.Xhosa,
    QLocale.Yiddish,
    QLocale.Zulu,
    QLocale.Armenian,
    QLocale.Breton,
    QLocale.French,
    QLocale.Portuguese,
    QLocale.Filipino,
    QLocale.Tigrinya,
    QLocale.Walloon,
    QLocale.Icelandic,
  ],
  '3': [
    QLocale.Latvian,
    QLocale.Divehi,
    QLocale.Inuktitut,
    QLocale.Inupiak,
    QLocale.Irish,
    QLocale.Manx,
    QLocale.Maori,
    QLocale.NorthernSami,
    QLocale.Samoan,
    QLocale.Sanskrit,
    QLocale.Slovak,
    QLocale.Czech,
    QLocale.Macedonian,
    QLocale.Lithuanian,
    QLocale.Bosnian,
    QLocale.Belarusian,
    QLocale.Croatian,
    QLocale.Russian,
    QLocale.Serbian,
    QLocale.Ukrainian,
    QLocale.Polish,
    QLocale.Romanian,
    QLocale.Tagalog,
  ],
  '4': [
    QLocale.Gaelic,
    QLocale.Slovenian,
    QLocale.Maltese,
  ],
  '5': [
    QLocale.Welsh,
  ],
  '6': [
    QLocale.Maltese,
    QLocale.Arabic,
  ]
}

def get_nplurals(locale):
    l = QLocale(locale)
    for nplural in nplurals.keys():
        if l.language() in nplurals[nplural]:
            return nplural
    return 0

class TSFormat:
    def __init__(self, conf):
        self.conf = conf
        self.tsfilename = conf["file"]
        if not os.path.isfile(conf["file"]):
            self.createNewTS()
        self.tscontent = self.parse(self.tsfilename)
        self.savedcontent = [TSEntry(x) for x in self.tscontent]

    def createNewTS(self):
        template = ET.parse(self.conf["template"])
        content = template.getroot()
        root = ET.Element('TS')
        for context in content:
            if context.tag == "context":
                for item in context:
                    if item.tag == "message":
                        numerus = item.get('numerus') == 'yes'
                        for child in item:
                            if child.tag == "translation":
                                child.text = ""
                                if numerus:
                                    item.remove(child)
                                    child = ET.Element('translation')
                                    for i in range(0, int(get_nplurals(self.conf['lang']))):
                                        print("numerusform")
                                        child.append(ET.Element('numerusform'))
                                    item.append(child)
                                break
            root.append(context)
        with open(self.tsfilename, "w+") as f:
            f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            f.write("<!DOCTYPE TS>")
            f.write(ET.tostring(root).decode("utf-8"))

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
                                    child.clear()
                                    unfinished = False
                                    for i in range(0, int(get_nplurals(self.conf['lang']))):
                                        e = ET.Element('numerusform')
                                        e.text = msgstrs[i]
                                        child.append(e)
                                        unfinished = unfinished or msgstrs[i] == ''
                                    if unfinished:
                                        child.set('type', 'unfinished')
                                else:
                                    if msgstrs[0] != "":
                                        child.clear()
                                    else:
                                        child.set('type', 'unfinished')
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
