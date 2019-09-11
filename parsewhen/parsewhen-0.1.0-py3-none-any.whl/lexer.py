class Lexer:

    def __init__(self, text):
        self.text = text
        self._start = 0
        self._cursor = 0

    @property
    def size(self):
        return len(self.text)

    @property
    def eof(self):
        return self.cursor == self.size

    @property
    def cursor(self):
        return bound(self._cursor, 0, self.size)

    @cursor.setter
    def cursor(self, value):
        self._cursor = bound(value, 0, self.size)
        return None

    @property
    def start(self):
        return bound(self._start, 0, self.size)

    @start.setter
    def start(self, value):
        self._start = bound(value, 0, self.size)
        return None

    @property
    def char(self):
        return self.text[self.cursor].lower()

    @property
    def step(self):
        while not self.eof:
            yield self.char
            self.cursor += 1

    @property
    def slice(self):
        if self.start == self.cursor:
            text = self.text[self.cursor]
        else:
            text = self.text[self.start:self.cursor]
        return text

    def previous(self, length=1):
        pos = bound(self.cursor - length, 0, self.size)
        return self.text[pos: self.cursor].lower()

    def next(self, length=1):
        pos = bound(self.cursor + length, 0, self.size)
        return self.text[self.cursor: pos].lower()

    def move(self, direction=1, update=False):
        self.cursor += direction
        if update:
            self.start = self.cursor
        return None

    def consume(self, chars, update=True):
        while self.char in chars:
            self.move()
            if update:
                self.start = self.cursor
        return None

    def consumewhile(self, expression, update=True):
        while expression(self.char):
            self.move(update=update)
        return None


def bound(value, _min=0, _max=100):
    return sorted([value, _min, _max])[1]
