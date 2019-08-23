from datetime import datetime
from typing import List

from .adresses import Adresses


class EMail:
    def __init__(self,
                 date: datetime,
                 subject: str,
                 from_: str,
                 to: List[str],
                 attachments: List[str] = None,
                 reply_to: str = None,
                 cc: List[str] = None,
                 bcc: List[str] = None,
                 forwards: List[int] = None,
                 replies: List[int] = None):
        self.date = date
        self.subject = subject
        self.from_ = from_
        self.to = to
        self.attachments = attachments
        self.reply_to = reply_to
        self.cc = cc
        self.bcc = bcc
        self.forwards = forwards
        self.replies = replies
        self.excerpt = None

    def to_line(self, adresses: Adresses) -> str:
        to = adresses.short_names(self.to)
        text = self.subject
        return f'{self.date} {self.from_}->{to} {text}'
