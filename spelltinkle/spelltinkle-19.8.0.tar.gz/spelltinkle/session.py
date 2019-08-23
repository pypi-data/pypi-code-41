import json
import os
from time import time
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional

from .input import InputHandler
from .keys import keynames, doubles, repeat, again
from .config import conf
from .document import Document
from .text import TextDocument
from .screen import Screen
from .mail.addresses import Addresses
from .mail.client import MailClient


class Session:
    def __init__(self,
                 filenames: List[str],
                 scr: Screen,
                 test: bool = False) -> None:
        self.scr = scr
        self.test = test
        self.folder = conf.home
        self.folder.mkdir(exist_ok=True)

        data = self.read()
        self.positions: Dict[Path, Tuple[int, int]] = data.get('positions', {})
        self.lastsearchstring = data.get('lastsearchstring', '')

        self.docs: List[Document] = []
        if filenames:
            for filename in filenames:
                doc = TextDocument(self)
                doc.read(filename)
                self.docs.append(doc)
        else:
            self.docs.append(TextDocument(self))

        self.lastkey = ''
        self.lasttime = 0.0
        self.memory = ['']
        self.chars = ''
        self.failed = False
        self.xclip = b''
        self._addresses: Optional[Addresses] = None
        self.mail_clients: Dict[str, MailClient] = {}

    def addresses(self):
        if self._addresses is None:
            self._addresses = Addresses(self.folder / 'mail/addresses.csv')
        return self._addresses

    def log(self, *args, **kwargs):
        with open(self.folder / 'log', 'a') as f:
            print(*args, **kwargs, file=f)

    @property
    def doc(self) -> Document:
        return self.docs[-1]

    def run(self) -> bool:
        import asyncio
        self.loop = asyncio.new_event_loop()
        self.loop.set_exception_handler(self.error)
        # self.loop.add_signal_handler(signal.SIGWINCH, self.resize)
        self.update()

        if self.test:
            self.loop.call_soon(self.inputtest)
        else:
            from spelltinkle.backup import Backup
            Backup(self)
            self.loop.add_reader(0, self.input1)

        self.loop.run_forever()
        self.loop.close()
        return self.failed

    def error(self, loop, context):
        import traceback
        txt = repr(context) + '\n' + traceback.format_exc()
        if self.test:
            print('\n', txt)
            self.loop.stop()
            self.failed = True
        else:
            for doc in self.docs:
                if doc.path:
                    old = doc.path
                    import tempfile
                    fd, name = tempfile.mkstemp()
                    os.close(fd)
                    doc.path = Path(name)
                    doc.write()
                    doc.path = old
            for doc in self.docs:
                if doc.name == '[error]':
                    self.docs.remove(doc)
                    break
            else:
                doc = TextDocument()
                doc.name = '[error]'
                doc.set_session(self)
            self.docs.append(doc)
            doc.change(0, 0, 0, 0, txt.splitlines())
            self.update()

    def resize(self) -> None:
        self.scr.resize()
        for doc in self.docs:
            doc.changes = 42
        self.update()

    def update(self) -> None:
        for doc in self.docs[-1:]:
            doc.view.update(self)
            if doc.changes:
                doc.color.run(self.loop)
            doc.changes = 0

    def draw_colors(self) -> None:
        doc = self.docs[-1]
        doc.changes = 42
        doc.view.update(self)
        doc.changes = 0

    def inputtest(self) -> None:
        self.input1()
        if self.loop.is_running():
            self.loop.call_soon(self.inputtest)

    def input1(self, key: str = '') -> None:
        if not key:
            key = self.scr.input()
            if key == 'unknown':
                return

        if key == 'resize':
            self.resize()
            return

        doc = self.docs[-1]
        handler = doc.handler or doc

        if len(key) == 1:
            self.chars += key
            newdoc = handler.insert_character(key)
        else:
            newdoc, key = self.input2(key, handler)
            if key == 'unknown':
                return
            doc.completion.stop()
            doc.completion.active = False

        if newdoc:
            newdoc.set_session(self)
            newdoc.changes = 42
            self.docs.append(newdoc)

        self.lastkey = key
        self.lasttime = time()
        if len(key) > 1:
            self.chars = ''
        self.update()

    def input2(self, key: str,
               handler: InputHandler) -> Tuple[Optional[Document], str]:
        if key in doubles:
            key2 = self.scr.input()
            key = doubles[key].get(key2, 'unknown')
            if key == 'unknown':
                return None, 'unknown'
        else:
            key = keynames.get(key, key)
            if key[0] == '^':
                return None, 'unknown'

        if key in again and key == self.lastkey:
            key += '_again'
        elif (key in repeat and key == self.lastkey and
              time() < self.lasttime + 0.3):
            key += key
        method = getattr(handler, key, None)
        if method is None:
            newdoc = handler.unknown(key)
        else:
            newdoc = method()

        if key.endswith('_again'):
            key = key[:-6]
        return newdoc, key

    def read(self) -> Dict[str, Any]:
        path = self.folder / 'session.json'
        if path.is_file():
            with open(path) as fd:
                data = json.load(fd)
                data['positions'] = {Path(path): tuple(pos)
                                     for path, pos
                                     in data['positions'].items()}
        else:
            data = {'positions': {}}
        return data

    def save(self) -> None:
        data = self.read()
        for doc in self.docs:
            if doc.path is not None:
                data['positions'][doc.path] = doc.view.pos
        data['positions'] = {str(path): pos
                             for path, pos
                             in data['positions'].items()}
        data['lastsearchstring'] = self.lastsearchstring
        with open(self.folder / 'session.json', 'w') as fd:
            json.dump(data, fd)
