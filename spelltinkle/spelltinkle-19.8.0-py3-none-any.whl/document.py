import os
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, List, Optional, Tuple

from .view import View
from .history import History
from .input import InputHandler
from .color import Color, PygmentsFlake8Color
from .complete import Completion
from .search import Search
from .utils import tolines
if TYPE_CHECKING:
    from .session import Session  # noqa


class Document(InputHandler):
    def __init__(self, session: 'Session' = None):
        self.lines = ['']
        self.modified = False
        self.backup_needed = True
        self.changes: int = 0
        self.view = View(self)
        self.history = History()
        self.path: Optional[Path] = None
        self._name = '[no name]'
        self.mode = 'Unknown'
        self.timestamp = -1000000000.0
        self.color: Color = PygmentsFlake8Color(self)
        self.completion = Completion()
        self.handler: Optional[InputHandler] = None
        self.session: Session
        if session:
            self.set_session(session)

    @property
    def name(self) -> str:
        if self.path:
            return self.path.name
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        assert self.path is None

    def log(self, *args, **kwargs):
        self.session.log(*args, **kwargs)

    def set_session(self, session: 'Session') -> None:
        self.session = session
        self.view.set_screen(session.scr)

    def build(self, w: int) -> List[Tuple[int, int, int]]:
        lines = []
        for r, line in enumerate(self.lines):
            c = len(line)
            for i in range(1 + c // w):
                lines.append((r, i * w, min((i + 1) * w, c)))
        return lines

    def change(self, r1: int, c1: int, r2: int, c2: int,
               lines: List[str],
               remember: bool = True):
        if c1 == c2 and r1 == r2 and lines == ['']:
            return
        self.color.stop()
        c3 = c1
        r3 = r1
        if c1 != c2 or r1 != r2:
            oldlines = self.delete_range(c1, r1, c2, r2)
        else:
            oldlines = ['']
        if lines != ['']:
            self.insert_lines(c1, r1, lines)
            r3 = r1 + len(lines) - 1
            if r3 == r1:
                c3 = c1 + len(lines[0])
            else:
                c3 = len(lines[-1])

        self.modified = True
        self.backup_needed = True
        if remember:
            change = (c1, r1, c2, r2, c3, r3, lines, oldlines)
            self.history.append(change)
        self.color.update(c1, r1, c2, r2, lines)
        self.changes = 42  # (r1, r2, r3)
        self.view.move(r3, c3)
        return oldlines

    def insert_lines(self, c: int, r: int, lines: List[str]):
        start = self.lines[r][:c]
        end = self.lines[r][c:]
        self.lines[r] = start + lines[0]
        self.lines[r + 1:r + 1] = lines[1:]
        self.lines[r + len(lines) - 1] += end

    def delete_range(self, c1: int, r1: int, c2: int, r2: int):
        start1 = self.lines[r1][:c1]
        end1 = self.lines[r1][c1:]
        start2 = self.lines[r2][:c2]
        end2 = self.lines[r2][c2:]
        if r1 == r2:
            oldlines = [start2[c1:]]
            self.lines[r1] = start1 + end2
        else:
            oldlines = [end1]
            oldlines.extend(self.lines[r1 + 1:r2])
            oldlines.append(start2)
            self.lines[r1] = start1
            del self.lines[r1 + 1:r2 + 1]
            self.lines[r1] += end2
        return oldlines

    def read(self, filename: str) -> None:
        self.path = Path(filename)
        if ':' in filename:
            filename, row = filename.rsplit(':', 1)
            self.path = Path(filename)
            r = int(row) - 1
            c = 0
        else:
            r, c = self.session.positions.get(self.path, (0, 0))
        try:
            with open(self.path, encoding='UTF-8') as fd:
                lines = tolines(fd)
        except FileNotFoundError:
            return
        self.change(0, 0, 0, 0, lines, remember=False)
        self.modified = False
        self.timestamp = self.path.stat().st_mtime
        self.view.move(r, c)

    def enumerate(self, r: int = 0, c: int = 0, direction: int = 1):
        if direction == 1:
            while r < len(self.lines):
                yield r, c, self.lines[r][c:]
                r += 1
                c = 0
        else:
            yield r, 0, self.lines[r][:c]
            while r >= 1:
                r -= 1
                yield r, 0, self.lines[r]

    def get_range(self, r1: int, c1: int, r2: int, c2: int) -> List[str]:
        lines = []
        for r, c, line in self.enumerate(r1, c1):
            if r == r2:
                lines.append(line[:c2 - c])
                return lines
            lines.append(line)
        assert False

    def up(self) -> None:
        self.view.move(max(0, self.view.r - 1), None)

    def down(self) -> None:
        self.view.move(self.view.r + 1, None)

    def down1(self) -> None:
        view = self.view
        if len(view.lines) > view.y + 1:
            r, c1, c2 = view.lines[view.y + 1]
            c = c1 + view.x
            if c > c2:

                c = None
            self.view.move(r, c)

    def scroll_up(self) -> None:
        y1 = self.view.y1
        if y1 == 0:
            return
        r = self.view.r
        if self.view.y == y1 + self.view.text.h - 1:
            r -= 1
            if r < 0:
                return
        self.view.y1 -= 1
        self.view.move(r, None)

    def scroll_down(self) -> None:
        y1 = self.view.y1
        if y1 == len(self.view.lines) - 1:
            return
        r = self.view.r
        if self.view.y == y1:
            r += 1
        self.view.y1 += 1
        self.view.move(r, None)

    def left(self) -> None:
        self.view.move(*self.view.prev())

    def right(self) -> None:
        self.view.move(*self.view.next())

    def ctrl_up(self, dir='up') -> None:
        if self.view.mark:
            mark = self.view.mark
            pos = self.view.pos
            if (mark > pos) ^ (dir in ['down', 'right']):
                getattr(self, dir)()
            else:
                self.mark()
                self.view.move(*mark)
        else:
            self.mark()
            getattr(self, dir)()

    def ctrl_down(self) -> None:
        self.ctrl_up('down')

    def ctrl_left(self) -> None:
        self.ctrl_up('left')

    def ctrl_right(self) -> None:
        self.ctrl_up('right')

    def mark_word(self) -> None:
        r, c = self.view.pos
        line = self.lines[r]
        n = len(line)
        if n == 0:
            return
        if c == n:
            c -= 1

        for c1 in range(0, c + 1):
            if line[c1:c + 1].isidentifier():
                break
        else:
            return

        for c2 in range(c + 1, n + 1):
            if not line[c1:c2].isidentifier():
                c2 -= 1
                break

        if c2 > c1:
            self.view.mark = r, c1
            self.view.move(r, c2, later=False)
            self.copy()

    def mouse1_clicked(self) -> None:
        x, y = self.session.scr.position
        if y == 0:
            for i, c in enumerate(self.view.tabcolumns):
                if c > x:
                    if i > 1:
                        docs = self.session.docs
                        docs.append(docs.pop(-i))
                        docs[-1].view.set_screen(self.session.scr)
                        docs[-1].changes = 42
                    break
        else:
            self.view.mouse(x, y)

    mouse1_pressed = mouse1_clicked

    def mouse1_released(self) -> None:
        x, y = self.session.scr.position
        if y > 0:
            self.mark()
            self.view.mouse(x, y)
            self.xselect()

    def xselect(self) -> None:
        r1, c1, r2, c2 = self.view.marked_region()
        lines = self.get_range(r1, c1, r2, c2)
        txt = '\n'.join(lines).encode()
        try:
            p = subprocess.Popen(['xclip', '-i'], stdin=subprocess.PIPE)
        except FileNotFoundError:
            self.session.xclip = txt
        else:
            p.communicate(txt)

    def home(self) -> None:
        self.view.move(None, 0)

    def homehome(self) -> None:
        self.view.move(0, 0)

    def end(self) -> None:
        self.view.move(None, len(self.lines[self.view.r]))

    def endend(self) -> None:
        self.view.move(len(self.lines) - 1, len(self.lines[-1]))

    def page_up(self) -> None:
        self.view.move(max(0, self.view.r - self.view.text.h), None)

    def page_down(self) -> None:
        self.view.move(self.view.r + self.view.text.h, None)

    def copy(self) -> None:
        if not self.view.mark:
            return
        r1, c1, r2, c2 = self.view.marked_region()

        self.color.stop()  # next two lines are a bit dangerous!
        lines = self.delete_range(c1, r1, c2, r2)
        self.insert_lines(c1, r1, lines)

        self.session.memory = lines
        self.xselect()

    def search_forward(self) -> None:
        self.handler = Search(self)

    def search_backward(self) -> None:
        self.handler = Search(self, -1)

    def view_files(self) -> 'Document':
        from .filelist import FileList
        return FileList()

    def write(self) -> Optional['Document']:
        if self.path is None:
            return self.write_as()

        self._write(self.path)
        self.modified = False
        self.timestamp = self.path.stat().st_mtime
        self.changes = 42
        return None

    def _write(self, path: Path) -> None:
        with open(path, 'w') as f:
            for line in self.lines[:-1]:
                print(line.rstrip(), file=f)
            if self.lines[-1]:
                print(self.lines[-1], file=f, end='')

    def write_as(self) -> 'Document':
        from spelltinkle.fileinput import FileInputDocument
        return FileInputDocument('./'
                                 if self.path is None
                                 else f'{self.path.parent}/',
                                 action='write as')

    def open(self):
        from .fileinput import FileInputDocument

        path = ''

        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            if r1 == r2:
                path = self.lines[r1][c1:c2]
                path = os.path.expandvars(path)
                path = os.path.expanduser(path)
                self.view.mark = None

        if not path:
            if self.path:
                path = f'{self.path.parent}/'
            else:
                path = './'

        return FileInputDocument(path)

    def help(self):
        from spelltinkle.help import HelpDocument
        return HelpDocument()

    def esc(self):
        self.view.mark = None
        self.changes = 42

    def mark(self):
        self.view.mark = self.view.pos

    def quit(self):
        if self.modified and self.path is not None:
            self.write()
        self.color.stop()
        self.session.save()
        self.session.docs.remove(self)
        if len(self.session.docs) == 0:
            self.session.loop.stop()
        else:
            self.session.docs[-1].changes = 42
            self.session.update()

    def quit_all(self):
        for doc in self.session.docs[:]:
            doc.quit()

    def command(self):
        from .command import Command
        self.handler = Command(self)

    def game(self):
        from spelltinkle.game import Game
        return Game(self.session)

    def code_analysis(self):
        errors = self.color.report
        if len(errors) == 0:
            return
        pos0 = self.view.pos
        for pos, txt in errors:
            if pos > pos0:
                break
        else:
            pos, txt = errors[0]
        self.view.move(*pos)
