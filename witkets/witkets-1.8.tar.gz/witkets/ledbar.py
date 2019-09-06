#!/usr/bin/env python3

from enum import Enum
from tkinter import *
from tkinter.ttk import *

_PADDING = 3


class LEDBar(Canvas):
    """10-level LED Bar widget.
        
       Options (all have default values):
          - coloron --- Color representing ON state
          - coloroff --- Color representing OFF state
          - number --- Level (0 to 10)
          - All :code:`Canvas` widget options (width, height, background etc.)
        
       Forms of access:
          >>> from witkets.ledbar import LEDBar
          >>> ledbar= LEDBar(coloron='#008')
          >>> ledbar['coloroff'] = '#CCC'
          >>> led.config(number = 5)
    """

    def __init__(self, master=None, coloron='green', coloroff='red',
                 number=0, **kw):
        # LED specifics
        self._widgetkeys = ('coloron', 'coloroff', 'number')
        self._coloron = coloron
        self._coloroff = coloroff
        self._number = number
        # Canvas
        if 'highlightthickness' not in kw:
            kw['highlightthickness'] = 0
        if 'width' not in kw:
            kw['width'] = 30
        if 'height' not in kw:
            kw['height'] = 100
        if 'background' not in kw:
            kw['background'] = '#FFF'
        Canvas.__init__(self, master, kw)
        self._light = None
        # Geometry
        self._width = int(self['width'])
        self._height = int(self['height'])
        # Highlight thickness
        self._draw()

    def __setitem__(self, key, val):
        if key in self._widgetkeys:
            self.__setattr__('_' + key, val)
        else:
            Canvas.__setitem__(self, key, val)
            self._width = int(self['width'])
            self._height = int(self['height'])
        self.redraw()

    def __getitem__(self, key):
        if key in self._widgetkeys:
            return getattr(self, '_' + key)
        else:
            return Canvas.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in kw:
            if key in self._widgetkeys:
                self.__setattr__('_' + key, kw[key])
                kw.pop(key, False)
        Canvas.config(self, **kw)
        self.redraw()

    def redraw(self):
        """Redraws the LED widget"""
        self.delete("all")
        self._draw()

    def _draw(self):
        w, h = (self._width, self._height)
        p = _PADDING
        c = (1, 1, w - 1, h - 1)
        hn = h / 31
        self.create_rectangle(*c)
        for i in range(10):
            fill = self._coloron if self._number > i else self._coloroff
            y1 = int(hn * (3 * i + 1))  # h * (3*x + 1) / 31
            y2 = int(hn * 3 * (i + 1))  # h * 3 * (x+1) / 31
            c = (p, h - y1, w - p, h - y2)
            self.create_rectangle(fill=fill, *c)


if __name__ == '__main__':
    root = Tk()
    root.config(borderwidth=10)
    ledbar = LEDBar(root)
    ledbar['background'] = '#FFF'
    ledbar['number'] = 5
    ledbar.pack()
    # led.bind('<Button-1>', toggle)
    root.mainloop()
