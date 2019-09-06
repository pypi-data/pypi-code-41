#!/usr/bin/env python3

from tkinter.scrolledtext import ScrolledText
from witkets.ipytext import IPyText


class PyScrolledText(ScrolledText, IPyText):
    """Text view with syntax highlighting for Python code
        
       Options (all have default values):
          - All :code:`Text` widget options
    """

    def __init__(self, master=None, text='', **kw):
        ScrolledText.__init__(self, master, **kw)
        IPyText.__init__(self, baseclass=ScrolledText, text=text)

    def __setitem__(self, key, val):
        IPyText.__setitem__(self, key, val)

    def __getitem__(self, key):
        return IPyText.__getitem__(self, key)


if __name__ == '__main__':
    import tkinter as tk

    root = tk.Tk()
    pyedit = PyScrolledText(root)
    pyedit['text'] = 'if True: x = 10 #wow!'
    pyedit.pack()
    root.mainloop()
