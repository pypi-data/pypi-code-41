import subprocess
import textwrap
from pathlib import Path
from typing import List, Optional, Callable

from .document import Document
from .keys import aliases, typos
from .complete import complete_word
from .utils import tolines


class TextDocument(Document):
    completions = None

    def insert_character(self, char) -> None:
        r, c = self.view.pos
        for key in typos:
            if self.session.chars.endswith(key):
                self.change(r, c - len(key) + 1, r, c, [typos[key]])
                self.session.chars = ''
                return

        self.change(r, c, r, c, [char])
        self.completion.run(self, r, c, self.session.loop)

    def mouse2_clicked(self) -> None:
        x, y = self.session.scr.position
        if y == 0:
            return
        r, c = self.view.mouse(x, y)
        try:
            txt = subprocess.check_output(['xclip', '-o'])
        except FileNotFoundError:
            txt = self.session.xclip
        lines = tolines(line + '\n' for line in txt.decode().split('\n'))
        self.change(r, c, r, c, lines[:-1])
        self.view.mark = None

    def bs(self) -> None:
        r2, c2 = self.view.pos
        if self.lines[r2][:c2].isspace():
            c1 = (c2 - 1) // 4 * 4
            r1 = r2
        else:
            r1, c1 = self.view.prev()
        self.change(r1, c1, r2, c2, [''])

    def upper(self, func: Callable[[str], str] = str.upper) -> None:
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            self.view.mark = None
        else:
            r1, c1 = self.view.pos
            r2, c2 = self.view.next()
        lines = self.change(r1, c1, r2, c2, [''])
        self.change(r1, c1, r1, c1, [func(line) for line in lines])

    def lower(self) -> None:
        self.upper(str.lower)

    def delete(self) -> None:
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            lines = self.change(r1, c1, r2, c2, [''])
            self.session.memory = lines
            self.view.mark = None
        else:
            r1, c1 = self.view.pos
            r2, c2 = self.view.next()
            self.change(r1, c1, r2, c2, [''])

    def rectangle_delete(self) -> None:
        r1, c1, r2, c2 = self.view.marked_region()
        if c1 == c2:
            return
        if c2 < c1:
            c1, c2 = c2, c1
        lines = []
        for r in range(r1, r2 + 1):
            line = self.lines[r]
            n = len(line)
            if c1 >= n:
                continue
            c3 = min(n, c2)
            line = self.change(r, c1, r, c3, [''])[0]
            lines.append(line)

        self.session.memory = lines
        self.view.mark = None
        self.changed = 42

    def rectangle_insert(self) -> None:
        r1, c1, r2, c2 = self.view.marked_region()
        if c2 < c1:
            c1, c2 = c2, c1
        line = self.session.memory[0]
        for r in range(r1, r2 + 1):
            n = len(self.lines[r])
            if n >= c2:
                self.change(r, c1, r, c2, [line])

        self.view.mark = None
        self.changed = 42

    def indent(self, direction=1) -> None:
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            if c2 > 0:
                r2 += 1
        else:
            r1 = self.view.r
            r2 = r1 + 1
        if direction == 1:
            for r in range(r1, r2):
                self.change(r, 0, r, 0, ['    '])
        else:
            for line in self.lines[r1:r2]:
                if line and not line[:4].isspace():
                    return
            for r in range(r1, r2):
                self.change(r, 0, r, min(4, len(self.lines[r])), [''])
            r, c = self.view.mark
            self.view.mark = r, min(c, len(self.lines[r]))
            self.view.move(*self.view.pos)

    def dedent(self) -> None:
        self.indent(-1)

    def undo(self) -> None:
        self.history.undo(self)

    def redo(self) -> None:
        self.history.redo(self)

    def paste(self) -> None:
        r, c = self.view.pos
        self.change(r, c, r, c, self.session.memory)
        self.view.mark = None

    def delete_to_end_of_line(self, append: bool = False) -> None:
        r, c = self.view.pos
        if (r, c) == self.view.next():
            return
        line = self.lines[r]
        if c == 0 and line.strip() == '' and r < len(self.lines) - 1:
            lines = self.change(r, 0, r + 1, 0, [''])
        elif c == len(line):
            lines = self.change(r, c, r + 1, 0, [''])
        else:
            lines = self.change(r, c, r, len(line), [''])
        if append:
            if self.session.memory[-1] == '':
                self.session.memory[-1:] = lines
            else:
                self.session.memory.append('')
        else:
            self.session.memory = lines

    def delete_to_end_of_line_again(self) -> None:
        self.delete_to_end_of_line(True)

    def enter(self) -> None:
        r, c = self.view.pos
        self.change(r, c, r, c, ['', ''])
        self.view.pos = (r + 1, 0)
        s = self.lines[r][:c]
        if s and not s.isspace():
            self.indent_line()

    def normalize_space(self) -> None:
        r, c = self.view.pos
        line = self.lines[r]
        n = len(line)
        c1 = len(line[:c].rstrip())
        c2 = n - len(line[c:].lstrip())
        if c1 == c2:
            return
        if c2 < n:
            if not (line[c2] in ')]}' or
                    c1 > 0 and line[c1 - 1] in '([{'):
                c2 -= 1
        self.change(r, c1, r, c2, [''])
        self.view.move(r, c1)

    def complete(self) -> None:
        complete_word(self)

    def jedi(self) -> Optional[Document]:
        import jedi
        from jedi import settings
        settings.case_insensitive_completion = False
        # from spelltinkle.fromimp import complete
        r, c = self.view.pos
        s = jedi.Script('\n'.join(self.lines), r + 1, c, '')
        defs = s.goto_definitions()
        self.view.message = f'Definitions found: {len(defs)}'
        if not defs:
            return None
        df = defs[0]
        self.log((df, df.module_path, df.name, df.type, df.module_name,
                  df.full_name))
        if df.module_path is None:
            self.view.move(df.line - 1, 0)
            return None

        path = Path(df.module_path)
        docs = self.session.docs
        for i, doc in enumerate(docs):
            if doc.path == path:
                docs.pop(i)
                doc.view.move(df.line - 1, 0)
                # doc.view.moved = (df.line, 0)
                # doc.changed = 42
                return doc

        doc = TextDocument()
        doc.read(f'{path}:{df.line}')
        return doc

    def format(self) -> None:
        r1 = self.view.r
        txt = self.lines[r1]
        r2 = r1 + 1
        while r2 < len(self.lines):
            line = self.lines[r2]
            if len(line) == 0 or line[0] == ' ':
                break
            r2 += 1
            txt += ' ' + line
        width = self.view.text.w - self.view.wn - 1
        lines = textwrap.wrap(txt, width - 3, break_long_words=False)
        self.change(r1, 0, r2 - 1, len(self.lines[r2 - 1]), lines)

    def tab(self) -> None:
        r, c = self.view.pos
        for key in aliases:
            if self.session.chars.endswith(key):
                self.change(r, c - len(key), r, c, [aliases[key]])
                self.session.chars = ''
                return

        if self.completion.active:
            self.change(r, c, r, c, [self.completion.word()])
            return

        self.indent_line()

    def indent_line(self) -> None:
        r, c = self.view.pos
        r0 = r - 1
        p: List[str] = []
        pend = False
        indent = None
        while r0 >= 0:
            line = self.lines[r0]
            if line and not line.isspace():
                n = len(line)
                for i in range(n - 1, -1, -1):
                    x = line[i]
                    j = '([{'.find(x)
                    if j != -1:
                        if not p:
                            if i < n - 1:
                                indent = i + 1
                                break
                            pend = True
                        elif p.pop() != ')]}'[j]:
                            indent = 0
                            # message
                            break
                    elif x in ')]}':
                        p.append(x)

                if indent is not None:
                    break

                if not p:
                    indent = len(line) - len(line.lstrip())
                    break

            r0 -= 1
        else:
            indent = 0
            line = '?'

        if pend or self.lines[r - 1].rstrip()[-1:] == ':':
            indent += 4

        line = self.lines[r]
        i = len(line) - len(line.lstrip())
        if i < indent:
            self.change(r, 0, r, 0, [' ' * (indent - i)])
        elif i > indent:
            self.change(r, 0, r, i - indent, [''])
        c += indent - i
        if c < indent:
            c = indent
        self.view.move(r, c)

    def replace2(self) -> None:
        pass

    def yapf(self) -> None:
        from yapf.yapflib.yapf_api import FormatCode

        r1, c1, r2, c2 = self.view.marked_region()
        if r2 > r1:
            if c2 > 0:
                r2 += 1
            c1 = 0
            c2 = 0

        lines = self.get_range(r1, c1, r2, c2)

        new, changed = FormatCode('\n'.join(lines))

        if changed:
            self.view.mark = None
            if r2 == r1:
                lines = [new.strip()]
            else:
                lines = new.splitlines()
        self.change(r1, c1, r2, c2, lines + [''])

    def spell_check(self) -> None:
        import enchant
        d = enchant.Dict('en_US')
        self.mark_word()
        r1, c1, r2, c2 = self.view.marked_region()
        self.view.mark = None
        word = self.lines[r1][c1:c2]
        if d.check(word):
            return
        self.change(r1, c1, r2, c2, [','.join(d.suggest(word))])

    def resolve_conflict(self):
        r, c = self.view.pos
        for r1 in range(r, -1, -1):
            if self.lines[r1].startswith('<<<<<<<'):
                break
        else:
            return
        for r3 in range(r, len(self.lines)):
            if self.lines[r3].startswith('>>>>>>>'):
                break
        else:
            return
        for r2 in range(r1 + 1, r3):
            if self.lines[r2].startswith('======='):
                break
        else:
            return
        if r == r2:
            return
        if r < r2:
            self.change(r2, 0, r3 + 1, 0, [''])
            self.change(r1, 0, r1 + 1, 0, [''])
        else:
            self.change(r3, 0, r3 + 1, 0, [''])
            self.change(r1, 0, r2 + 1, 0, [''])

    def diff(self):
        import difflib
        with open(self.path, encoding='UTF-8') as fd:
            lines = tolines(fd)
        s = difflib.SequenceMatcher(a=self.lines, b=lines)
        blocks = s.get_matching_blocks()
        b2 = blocks[-1]
        for b1 in blocks[-2::-1]:
            na = b2.a - (b1.a + b1.size)
            nb = b2.b - (b1.b + b1.size)
            if na or nb:
                self.change(b2.a, 0, b2.a, 0,
                            ['======='] +
                            lines[b2.b - nb:b2.b] +
                            ['>>>>>>> file on disk', ''])
                self.change(b2.a - na, 0, b2.a - na, 0,
                            ['<<<<<<< this document', ''])
            b2 = b1

    def usages(self) -> Optional[Document]:
        import jedi
        r, c = self.view.pos
        s = jedi.Script('\n'.join(self.lines), r + 1, c, '')
        usages = s.usages()
        if not usages:
            return None
        doc = TextDocument()
        doc.change(0, 0, 0, 0, [usage for usage in usages])
        return doc
