#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *


class NumericLabel(Label):
    """Label intended for displaying numeric values
    
       Options (all have default values):
         - numvariable --- Numeric Tk variable to stock value
         - format --- printf-like format to render number (plus %B and %H)
         - number --- Number to show
         - All :code:`Label` widget options
        
       Forms of access: 
          >>> from witkets.numericlabel import NumericLabel, 
          >>> lbl = NumericLabel(format='%B')
          >>> varLbl = IntVar()
          >>> lbl.config(numvariable = varLbl)  
          >>> lbl['number'] = 200
    """

    def __init__(self, master=None, numvariable=None, format='%.2f', number=0, 
                 **kw):
        Label.__init__(self, master, **kw)
        self._widgetKeys = ('numvariable', 'number', 'format')
        if not numvariable:
            self._var = DoubleVar()
        else:
            self._var = numvariable
        self._var.set(number)
        self._var.trace('w', self._show)
        self._format = format
        self._show()
        
    @staticmethod
    def format_bin(byte):
        """Bases binary data grouping nibbles"""
        bits = bin(byte)[2:]
        size = len(bits)
        if size % 4 > 0:
            size = size + 4 - (size % 4)
        bits = bits.zfill(size)
        msg = ''
        cursor_a = 0
        for i in range(size // 4):
            cursor_a = i * 4
            cursor_b = (i + 1) * 4
            msg += bits[cursor_a:cursor_b] + ' '
        return '0b ' + msg
        
    @staticmethod
    def format_hex(byte):
        """Format number as hexadecimal"""
        return '0x' + hex(byte)[2:].upper()
        
    def _show(self, *event):
        if self._format == '%B':
            self['text'] = self.format_bin(int(self._var.get()))
        elif self._format == '%H':
            self['text'] = self.format_hex(int(self._var.get()))
        else:
            self['text'] = self._format % self._var.get()
            
    # =====================================================================
    # Inherited Methods
    # =====================================================================
        
    def __setitem__(self, key, val):
        if key in self._widgetKeys:
            if key == 'number':
                self._var.set(val)
            elif key == 'numvariable':
                self._var = val
                self._var.trace('w', self._show)
            else:
                self.__setattr__('_' + key, val)
            self._show()
        else:
            Label.__setitem__(self, key, val)
        
    def __getitem__(self, key):
        if key in self._widgetKeys:
            if key == 'number':
                return self._var.get()
            elif key == 'numvariable':
                return self._var
            else:
                return self.__getattribute__('_' + key)
        else:
            return Label.__getitem__(self, key)
            
    def config(self, **kw):
        """Tk standard config method"""
        other_kw = {}
        for key in kw:
            if key == 'number':
                self._var.set(kw[key])
            elif key == 'numvariable':
                self._var = kw[key]
                self._var.trace('w', self._show)
            elif key in self._widgetKeys:
                self[key] = kw[key]
            else:
                other_kw[key] = kw[key]
        Label.config(self, **other_kw)
        self._show()


# =====================================================================
# Test script
# =====================================================================
        
if __name__ == '__main__':
    root = Tk()
    var = IntVar()
    a = NumericLabel(root, numvariable=var)
    a.pack(pady=10)
    a['format'] = '%X'
    a['number'] = 0xFA
    b = NumericLabel(root, format='%03d')
    b.pack(pady=10)
    b['numvariable'] = var
    c = NumericLabel(root, format='%B')
    c.pack(pady=10)
    c.config(numvariable=var)
    root.mainloop()