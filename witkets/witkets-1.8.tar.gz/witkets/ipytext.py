import tkinter as tk

try:
    from pygments import lex
    from pygments.lexers.python import Python3Lexer

    havePygments = True
except ImportError:
    import sys

    print('Pygments library not found. Syntax highlighting not available.',
          file=sys.stderr)
    havePygments = False


class IPyText(object):
    """Python highlighter mixin"""

    def __init__(self, baseclass, text=''):
        self.baseclass = baseclass
        self._widgetkeys = ('text',)
        self.baseclass.delete(self, '1.0', tk.END)  # initial text
        self.baseclass.insert(self, tk.END, text)
        self.bind("<KeyRelease>", self._update)
        self.config(font='Courier 14', tabs=40)
        self._config_tags()
        self._update()  # first time

    def _config_tags(self):
        self.tag_configure("Token.Comment.Single", foreground="#cccccc")
        self.tag_configure("Token.Keyword", font='Courier 14 bold')
        self.tag_configure("Token.Keyword.Constant", font='Courier 14 bold',
                           foreground='#0000A0')
        # Strings
        for suffix in ('Single', 'Double', 'Doc'):
            tag = "Token.Literal.String.%s" % suffix
            self.tag_configure(tag, foreground='#008000')

    def _update(self, *event):
        if not havePygments:
            return
        self.mark_set("range_start", "1.0")
        data = self.get("1.0", "end-1c")
        for token, content in lex(data, Python3Lexer()):
            self.mark_set("range_end", "range_start + %dc" % len(content))
            self.tag_add(str(token), "range_start", "range_end")
            self.mark_set("range_start", "range_end")

    def __setitem__(self, key, val):
        if key in self._widgetkeys:
            self.__setattr__('_' + key, val)
            if key == 'text':
                if not val:
                    val = ''
                self.baseclass.delete(self, '1.0', tk.END)
                self.baseclass.insert(self, tk.END, val)
            self._update()
        else:
            self.baseclass.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key in self._widgetkeys:
            if key == 'text':
                return self.baseclass.get(self, '1.0', tk.END)
            return getattr(self, '_' + key)
        else:
            return self.baseclass.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in kw:
            if key == 'text':
                self.baseclass.delete(self, '1.0', tk.END)
                self.baseclass.insert(self, tk.END, kw[key])
                kw.pop(key, False)
            elif key in self._widgetkeys:
                self.__setattr__('_' + key, kw[key])
                kw.pop(key, False)
        self._update()
        self.baseclass.config(self, **kw)
