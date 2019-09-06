#!/usr/bin/env python3

import tkinter as tk
from witkets.ipytext import IPyText


class PyText(tk.Text, IPyText):
    """Text view with syntax highlighting for Python code
        
       Options (all have default values):
          - All :code:`Text` widget options
    """

    def __init__(self, master=None, text='', **kw):
        tk.Text.__init__(self, master, **kw)
        IPyText.__init__(self, baseclass=tk.Text, text=text)

    def __setitem__(self, key, val):
        IPyText.__setitem__(self, key, val)

    def __getitem__(self, key):
        return IPyText.__getitem__(self, key)


if __name__ == '__main__':
    root = tk.Tk()
    pyedit = PyText(root)
    pyedit.pack()
    root.mainloop()
