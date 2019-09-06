#!/usr/bin/env python3

from enum import Enum
from tkinter import *
from tkinter.ttk import *


# TODO Use boolean variable type (BooleanVar)

class Shapes(Enum):
    """LED shapes (Round or Square)"""
    ROUND = 1
    SQUARE = 2


class LED(Canvas):
    """Digital (ON/OFF) LED widget.
        
       Options (all have default values):
          - coloron --- Color representing ON state
          - coloroff --- Color representing OFF state
          - shape --- Either led.Shapes.ROUND (default) or led.Shapes.SQUARE
          - boolean --- LED state
          - All :code:`Canvas` widget options (notably width and height)
        
       Forms of access:
          >>> from witkets.led import LED, Shapes
          >>> ...
          >>> led = LED(root, coloron='#008', shape=Shapes.SQUARE)
          >>> led['coloroff'] = '#CCC'
          >>> led.config(boolean = True)
    """

    def __init__(self, master=None, coloron='green', coloroff='red',
                 shape=Shapes.ROUND, boolean=False, **kw):
        # LED specifics
        self._widgetkeys = ('coloron', 'coloroff', 'shape', 'boolean')
        self._coloron = coloron
        self._coloroff = coloroff
        self._shape = shape
        self._boolean = boolean
        # Canvas
        if 'highlightthickness' not in kw:
            kw['highlightthickness'] = 0
        if 'width' not in kw:
            kw['width'] = 25
        if 'height' not in kw:
            kw['height'] = 25
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

    def toggle(self):
        """Toggles the LED state"""
        self['boolean'] = not self._boolean

    def redraw(self):
        """Redraws the LED widget"""
        if self._light:
            self.delete(self._light)
        self._draw()

    def _draw(self):
        fill = self._coloron if self._boolean else self._coloroff
        c = (1, 1, self._width - 1, self._height - 1)
        if self._shape == Shapes.ROUND:
            self._light = self.create_oval(fill=fill, *c)
        else:
            self._light = self.create_rectangle(fill=fill, *c)


if __name__ == '__main__':
    def toggle(evt):
        evt.widget.toggle()


    root = Tk()
    frame = Frame(root)
    leds = []
    for i in range(8):
        led = LED(frame, width=25, height=25)
        led.pack(side=LEFT, fill=BOTH, expand=1)
        led.bind('<Button-1>', toggle)
        leds.append(led)
        led['boolean'] = ((i % 2) == 0)
        if 4 <= i < 6:
            led['coloroff'] = '#CCC'
            led['coloron'] = '#00F'
        if i >= 6:
            led['shape'] = Shapes.SQUARE
    print('First led is: ' + str(leds[0]['boolean']))
    frame.pack(fill=BOTH, expand=1)
    root.mainloop()
