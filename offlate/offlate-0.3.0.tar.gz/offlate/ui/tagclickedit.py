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

import re
import sys
from urllib.parse import quote
import html

class TagClickEdit(QTextBrowser):
    def __init__(self, *args):
        QTextBrowser.__init__(self, *args)

    def createLinks(self):
        text = self.toHtml()
        for word_object in re.finditer(r'@[a-z]+{[^}]*}', text):
            rep = word_object.string[word_object.span()[0] : word_object.span()[1]]
            text = text.replace(rep, '<a href="#' + quote(html.unescape(rep)) + '">' + rep + '</a>')
        self.setHtml(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TagClickEdit()
    w.setText("GNU@tie{}Hello provides the @command{hello} command.")
    w.createLinks()
    w.show()
    sys.exit(app.exec_())
