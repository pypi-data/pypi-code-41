# -*- coding: utf-8 -*-
"""Quip objects. Contains filtering logic, but no API calls."""

import time
import click
from dataclasses import dataclass
from typing import Any, Dict, List

import quare.quip as quip


@dataclass
class Meta:
    """Quip stores metadata in a `meta` property. This is the base class for common properties."""

    id: str
    created_usec: int
    updated_usec: int


@dataclass
class FolderMeta(Meta):
    title: str
    color: str = "manila"
    parent_id: str = None
    creator_id: str = None


@dataclass
class ThreadMeta(Meta):
    link: str
    title: str
    author_id: str
    thread_class: Any = None
    sharing: str = None
    type: Any = None
    document_id: str = None


@dataclass
class QuipFolder:
    member_ids: List[str]
    children: List[Dict[str, str]]
    folder: Dict

    def __post_init__(self):
        """Unpack the folder dictionary into the meta field."""
        self.meta = FolderMeta(**self.folder)

    @property
    def child_threads(self):
        return self._filter_children("thread_id")

    @property
    def child_folders(self):
        return self._filter_children("folder_id")

    def _filter_children(self, key):
        return [child[key] for child in self.children if key in child]


@dataclass
class QuipMessage:
    """Represents a quip message."""

    id: str
    created_usec: int
    updated_usec: int
    text: str
    author_name: str
    author_id: str
    visible: str
    annotation: Dict = None
    parts: List[List[str]] = None
    like_user_ids: List[str] = None
    mention_user_ids: List[str] = None
    files: List[str] = None

    @classmethod
    def from_dict(cls, dict_val):
        return cls(**{k: v for k, v in dict_val.items() if k in cls.__annotations__})

    @property
    def created(self):
        return self._parse_time(self.created_usec)

    @property
    def updated(self):
        return self._parse_time(self.updated_usec)

    def _parse_time(self, usecs):
        return time.asctime(time.localtime(usecs / 1e6))

    def __hash__(self):
        """
        On the remote chance that we have two messages with the same created_usec,
        sum the characters in that message's ID and add it to the created_usec.
        Almost certainly a case of YAGNI.
        """
        return self.created_usec + sum([ord(c) for c in self.id])

    def print(self, style=True, thread=None):
        thread = f"| ({thread}) " if thread else ""
        msg_header = f"[{self.created} {thread}| @{self.author_name}]"
        msg_header = click.style(msg_header, bold=True) if style else msg_header
        click.echo(f"{msg_header} {self.text}")


@dataclass
class QuipThread:
    """A Quip Thread. Either a chat or document.

    Args:
        user_ids (List[str]): User IDs with access to this thread.
        shared_folder_ids (List[str]): List of QuipFolder IDs containing this thread.
        expanded_user_ids (List[str]): User IDs with access to this thread.
        invited_user_emails (List[str]): Emails of users with access to this thread.
        html (str): The contents as HTML, if this thread is a document.
        thread (Dict): Dictionary containing metadata
        meta (ThreadMeta): ThreadMeta instance containing metadata
        token (str): API access token.
    """

    user_ids: List[str]
    thread: Dict
    shared_folder_ids: List[str] = None
    expanded_user_ids: List[str] = None
    invited_user_emails: List[str] = None
    html: str = None

    def __post_init__(self):
        """Unpack the folder dictionary into the meta field."""
        self.meta = ThreadMeta(**self.thread)
        self.id = self.meta.id

        # Instance variables
        self.token = None

    @staticmethod
    def get_thread(token, room):
        """Instantiate a thread by calling the QuipAPI."""
        client = quip.QuipClient(token)
        thread_json = client.get_thread(room)
        return QuipThread(**thread_json)

    def get_messages(
        self, token=None, start_usec=1000, last_n=None, return_raw_json=False
    ):
        """Returns the most recent messages for this thread.

        Args:
            start_usec: Return all messages since this timestamp.
            last_n: An integer indicating the number of messages you want returned.
                This is distinct from the `count` param accepted by the Quip API,
                in that it is the total number of messages to return, not the
                total to return for a given request.

        Returns:
            A list of message dicts, sorted by their created date in ascending order
        """
        self.messages = []
        client = quip.QuipClient(token)
        COUNT = last_count = 200  # For the first iteration of the while loop
        last_usec = None

        while last_count == COUNT:
            # I think the non list comprehension version is equally unreadable
            message_dicts = [
                msg
                for msg in client.get_messages(
                    self.meta.id, max_created_usec=last_usec, count=last_n
                )
                if msg["created_usec"] > start_usec
            ]

            last_count = len(message_dicts)
            self.messages.extend(message_dicts)
            if last_count == last_n:
                break
        return self.messages

    def send_message(
        self,
        token=None,
        frame=None,
        content=None,
        silent=False,
        return_raw_json=False,
        parts=None,
    ) -> QuipMessage:
        """Send a message to this thread.

        Args:
            frame: Controls how Quip displays the message.
            body: An integer indicating the number of messages you want returned.
                This is distinct from the `count` param accepted by the Quip API,
                in that it is the total number of messages to return, not the
                total to return for a given request.

        Returns:
            A QuipMessage instance
        """
        client = quip.QuipClient(token)
        # Using the vendored library, note that it passes keywords to the api via **kwargs
        msg_dict = client.new_message(
            self.id, content=content, silent=silent, frame=frame, parts=parts
        )
        return QuipMessage.from_dict(msg_dict)
