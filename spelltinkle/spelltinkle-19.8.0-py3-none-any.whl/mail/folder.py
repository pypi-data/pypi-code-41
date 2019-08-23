from ..color import Color
from ..document import Document
from ..session import Session
from .client import MailClient


class MailFolderDocument(Document):
    def __init__(self,
                 name: str,
                 session: Session,
                 folder: str = 'INBOX'):
        Document.__init__(self)
        self.name = name
        self.session = session
        self.folder = folder
        if not self.client:
            session.mail_clients[name] = MailClient(name)
        self.mails = self.client.get_mails(folder)

        self.color = Color()

    @property
    def client(self):
        return self.session.mail_clients.get(self.name)

    def list(self):
        # self.color.colors = colors = []

        lines = [mail.to_line() for mail in self.mails]
        self.change(0, 0, len(self.lines) - 1, 0, lines)
        self.view.move(0, 0)
