#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk


class Spin(ttk.Frame):
    """Spin Box with features such as custom number formatting and 
       orientation.
        
       Options (all have default values):
          - circular --- Toggles circular increments and decrements
          - from --- Minimum numeric value
          - orientation --- Either tk.HORIZONTAL (default) or tk.VERTICAL 
            (constructor only)
          - numberformat --- The format applied to the number (default: '%d')
          - step --- Delta applied to the value when buttons are clicked
          - to --- Maximum numeric value
          - variable --- A Tk numeric variable to store the number
          - All :code:`Frame` widget options
    """

    def __init__(self, master=None, from_=0, to=100, step=1, numberformat='%d',
                 variable=None, circular=False, orientation=tk.HORIZONTAL, **kw):
        ttk.Frame.__init__(self, master, **kw)
        self._widgetKeys = ('from', 'to', 'step', 'numberformat', 'variable',
                            'circular')
        # Button plus
        self._buttonPlus = tk.Button(self, text='+', width=1)
        self._buttonPlus['command'] = self._handle_plus
        # Text and numeric variables
        self._textvariable = tk.StringVar()
        if not variable:
            self._var = tk.DoubleVar()
        else:
            self._var = variable
        self._var.trace('w', self._update)
        # Entry
        self.entry = ttk.Entry(self, textvariable=self._textvariable)
        self.entry['justify'] = tk.CENTER
        # Button minus
        self._buttonMinus = tk.Button(self, text='-', width=1)
        self._buttonMinus['command'] = self._handle_minus
        # Parameters (@TODO Add getattr and other access methods)
        self._min_value = from_
        self._max_value = to
        self._step = step
        self._numberformat = numberformat
        self._circular = circular
        # Initial value
        self._var.set(self._min_value)
        # Orientation
        if orientation == tk.HORIZONTAL:
            self.entry.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
            self._buttonMinus.pack(side=tk.LEFT, fill=tk.Y)
            self._buttonPlus.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self._buttonPlus.pack(fill=tk.X)
            self.entry.pack(expand=1, fill=tk.BOTH)
            self._buttonMinus.pack(fill=tk.X)
            self._buttonPlus['relief'] = tk.FLAT
            self._buttonMinus['relief'] = tk.FLAT

    # =====================================================================
    # Value read and write
    # =====================================================================

    def get(self):
        """Sets the numeric value of the entry"""
        return self._var.get()

    def set(self, value):
        """Get the numeric value of the entry"""
        self._var.set(value)

    # =====================================================================
    # Private Methods
    # =====================================================================

    def _update(self, *args):
        val = self._var.get()
        self._textvariable.set(self._numberformat % val)

    def _handle_plus(self):
        next_value = self._var.get() + self._step
        if next_value < self._max_value:
            self._var.set(next_value)
        elif not self._circular:
            self._var.set(self._max_value)
        else:
            self._var.set(self._min_value)

    def _handle_minus(self):
        next_value = self._var.get() - self._step
        if next_value > self._min_value:
            self._var.set(next_value)
        elif not self._circular:
            self._var.set(self._min_value)
        else:
            self._var.set(self._max_value)

    def _check_limits(self):
        value = self._var.get()
        if not value:
            self._var.set(self._min_value)
        elif value < self._min_value:
            self._var.set(self._min_value)
        elif value > self._max_value:
            self._var.set(self._max_value)

    # =====================================================================
    # Config methods
    # =====================================================================

    def _handle_witket_key(self, key, val):
        if key == 'variable':
            self._var = val
            self._var.trace('w', self._update)
            self._check_limits()
        elif key == 'from':
            self._min_value = val
            self._check_limits()
        elif key == 'to':
            self._max_value = val
            self._check_limits()
        else:
            self.__setattr__('_' + key, val)
            self._update()

    def __setitem__(self, key, val):
        if key in self._widgetKeys:
            self._handle_witket_key(key, val)
        else:
            ttk.Frame.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key in self._widgetKeys:
            if key == 'variable':
                return self._var
            elif key == 'from':
                return self._min_value
            elif key == 'to':
                return self._max_value
            else:
                return self.__getattribute__('_' + key)
        else:
            return ttk.Frame.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key, val in kw.iteritems():
            if key in self._widgetKeys:
                self._handle_witket_key(key, val)
                kw.pop(key, False)
        ttk.Frame.config(self, **kw)


if __name__ == '__main__':
    root = tk.Tk()
    spin1 = Spin(root)
    spin1.pack(side=tk.LEFT, padx=15)
    spin1.set(10)
    spin1.entry['width'] = 2
    spin2 = Spin(root, orientation=tk.VERTICAL, numberformat='%06.3f')
    spin2.pack(side=tk.LEFT, padx=15)
    spin2.entry['width'] = 7
    spin2.set(3.238)
    root.mainloop()
