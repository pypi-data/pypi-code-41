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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import enchant
import re
import sys

class SpellCheckEdit(QTextEdit):
    def __init__(self, lang, *args):
        QTextEdit.__init__(self, *args)
        try:
            self.dict = enchant.Dict(lang)
        except:
            self.dict = None
        self.highlighter = Highlighter(self.document())
        self.highlighter.setDict(self.dict)

    def contextMenuEvent(self, event):
        popup_menu = self.createStandardContextMenu()

        # Select the word under the cursor.
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        self.setTextCursor(cursor)

        if self.textCursor().hasSelection():
            text = self.textCursor().selectedText()
            if not self.dict.check(text):
                spell_menu = QMenu(self.tr('Spelling Suggestions'))
                nospell = QAction(self.tr('No Suggestions'))
                nospell.setEnabled(False)
                for word in self.dict.suggest(text):
                    action = QAction(word)
                    action.triggered.connect((lambda word: (lambda : self.correctWord(word)))(word))
                    spell_menu.addAction(action)
                # If there are suggestions, use the spell_menu. Otherwise, show
                # there is no suggestion.
                popup_menu.insertSeparator(popup_menu.actions()[0])
                if len(spell_menu.actions()) != 0:
                    popup_menu.insertMenu(popup_menu.actions()[0], spell_menu)
                else:
                    popup_menu.insertAction(popup_menu.actions()[0], nospell)

        popup_menu.exec_(event.globalPos())

    def correctWord(self, word):
        cursor = self.textCursor()
        cursor.beginEditBlock()

        cursor.removeSelectedText()
        cursor.insertText(word)

        cursor.endEditBlock()

class Highlighter(QSyntaxHighlighter):
    def __init__(self, *args):
        QSyntaxHighlighter.__init__(self, *args)

    def setDict(self, dico):
        self.dict = dico

    def highlightBlock(self, text):
        if self.dict == None:
            return

        format = QTextCharFormat()
        format.setUnderlineColor(Qt.red)
        format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        for word_object in re.finditer(r'\b[^\W\d_]+\b', text):
            if not self.dict.check(word_object.group()):
                self.setFormat(word_object.start(), word_object.end() - word_object.start(), format)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SpellCheckEdit()
    w.show()
    sys.exit(app.exec_())
