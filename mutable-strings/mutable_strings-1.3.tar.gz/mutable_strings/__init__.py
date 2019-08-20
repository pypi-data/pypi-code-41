
class MutStr:
    """Class of Mutable String and methods for it"""

    def __init__(self, string):
        self.str = bytearray(string, "utf-8")

    def __getitem__(self, val):
        return MutStr(self.str.decode()[val])

    def __setitem__(self, item, val):
        if isinstance(item, int):
            self.str[item:item + 1] = bytes(val, "utf-8")
        else:
            self.str[item] = bytes(val, "utf-8")
        return MutStr(self.str.decode())

    def __str__(self):
        return self.str.decode()

    def __repr__(self):
        return self.str.decode()

    def __add__(self, val):
        result = str(self.str.decode()) + str(val)
        return MutStr(result)

    def __len__(self):
        return len(self.str.decode())

    def __iter__(self):
        return iter(self.str.decode())

    def title(self):
        return MutStr(self.str.decode().title())

    def find(self, s, start=None, end=None):
        return MutStr(self.str.decode().find(s, start, end))

    def rfind(self, s, start=None, end=None):
        return MutStr(self.str.decode().rfind(s, start, end))

    def index(self, s, start=None, end=None):
        return MutStr(self.str.decode().index(s, start, end))

    def rindex(self, s, start=None, end=None):
        return MutStr(self.str.decode().rindex(s, start, end))

    def replace(self, old, new):
        return MutStr(self.str.decode().replace(old, new))

    def rreplace(self, old, new):
        try:
            place = self.str.decode().rindex(old)
            return MutStr(''.join((self.str.decode()[:place], new, self.str.decode()[place + len(old):])))
        except ValueError:
            return MutStr(self.str.decode())

    def split(self, symbol):
        return MutStr(self.str.decode().split(symbol))

    def isdigit(self):
        return MutStr(self.str.decode().isdigit())

    def isalpha(self):
        return MutStr(self.str.decode().isalpha())

    def isalnum(self):
        return MutStr(self.str.decode().isalnum())

    def islower(self):
        return MutStr(self.str.decode().islower())

    def isupper(self):
        return MutStr(self.str.decode().isupper())

    def isspace(self):
        return MutStr(self.str.decode().isspace())

    def istitle(self):
        return MutStr(self.str.decode().istitle())

    def upper(self):
        return MutStr(self.str.decode().upper())

    def lower(self):
        return MutStr(self.str.decode().lower())

    def startswith(self, s):
        return MutStr(self.str.decode().startswith(s))

    def endswith(self, s):
        return MutStr(self.str.decode().endswith(s))

    def join(self, arr):
        return MutStr(self.str.decode().join(arr))

    def ord(self, c):
        return MutStr(self.str.decode().ord(c))

    def chr(self, d):
        return MutStr(self.str.decode().chr(d))

    def capitalize(self):
        return MutStr(self.str.decode().capitalize())

    def center(self, width, fill=None):
        return self.str.decode().center(width, fill)

    def count(self, s, start=None, end=None):
        return MutStr(self.str.decode().count(s, start, end))

    def expandtabs(self, tabsize=None):
        return MutStr(self.str.decode().expandtabs(tabsize))

    def lstrip(self, c=None):
        return MutStr(self.str.decode().lstrip(c))

    def rstrip(self, c=None):
        return MutStr(self.str.decode().rstrip(c))

    def strip(self, c=None):
        return MutStr(self.str.decode().strip(c))

    def partition(self, sep):
        return MutStr(self.str.decode().partition(sep))

    def rpartition(self, sep):
        return MutStr(self.str.decode().rpartition(sep))

    def swapcase(self):
        return MutStr(self.str.decode().swapcase())

    def zfill(self, width=None):
        return MutStr(self.str.decode().zfill(width))

    def ljust(self, width, fillchar=" "):
        return MutStr(self.str.decode().ljust(width, fillchar))

    def rjust(self, width, fillchar=" "):
        return MutStr(self.str.decode().rjust(width, fillchar))

    def format(self, *args, **kwargs):
        return MutStr(self.str.decode().format(*args, **kwargs))