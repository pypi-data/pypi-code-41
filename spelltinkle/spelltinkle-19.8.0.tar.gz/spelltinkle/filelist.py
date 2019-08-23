from typing import Dict

from .document import Document
from .config import conf


class FileList(Document):
    def __init__(self) -> None:
        Document.__init__(self)
        self.name = '[list]'
        self.mail: Dict[str, str] = {}

    def set_session(self, session):
        Document.set_session(self, session)
        lines = [doc.name for doc in session.docs[::-1]]
        for key, name in zip('mM', conf.mail):
            lines.append(f'MAIL: {name}')
            self.mail[key] = name
        self.change(0, 0, 0, 0, lines + [''])
        self.view.move(2, 0)
        "save Saveall quit/del/bs enter copy open esc"

    def insert_character(self, c):
        if c.isdigit():
            i = int(c)
            if 0 < i < len(self.session.docs):
                return self.choose(i)
            else:
                c = 'mM'[i - len(self.session.docs)]
        if c == 'c':
            from spelltinkle.calender import CalenderDocument
            self.session.docs.pop()
            return CalenderDocument()
        if c in 'mM':
            from spelltinkle.mail.folder import MailFolderDocument
            self.session.docs.pop()
            name = self.mail[c]
            return MailFolderDocument(name, self.session)

    def choose(self, i):
        self.session.docs.pop()
        return self.session.docs.pop(-i)

    def enter(self):
        return self.choose(self.view.r + 1)

    def esc(self):
        return self.choose(1)

    def view_files(self):
        return self.insert_character('2')
