#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *


# TODO Use boolean variable type (BooleanVar)

class LogicSwitch(Canvas):
    """Digital (ON/OFF) switch widget.
        
       Options (all have default values):
          - coloron --- Color representing ON state
          - coloroff --- Color representing OFF state
          - boolean --- Initial state
          - orientation -- Either tkinter.VERTICAL or tkinter.HORIZONTAL
          - All :code:`Canvas` widget options (notably width and height)
        
       Forms of access:
          >>> from witkets.logicswitch import LogicSwitch
          >>> switch = LogicSwitch(coloron='#008')
          >>> switch['coloroff'] = '#CCC'
          >>> switch.config(boolean = True)  
    """

    def __init__(self, master=None, coloron='green', coloroff='red',
                 boolean=False, orientation=VERTICAL, **kw):
        self._widgetKeys = ('coloron', 'coloroff', 'boolean', 'orientation')
        if 'width' not in kw:
            kw['width'] = 25
        if 'height' not in kw:
            kw['height'] = 25
        if 'background' not in kw:
            kw['background'] = '#FFF'
        Canvas.__init__(self, master, kw)
        # Config
        self._coloron = coloron
        self._coloroff = coloroff
        self._orientation = orientation
        # State
        self._boolean = boolean
        self._draw()

    def __setitem__(self, key, val):
        if key in self._widgetKeys:
            self.__setattr__('_' + key, val)
        else:
            Canvas.__setitem__(self, key, val)
        self.redraw()

    def __getitem__(self, key):
        if key in self._widgetKeys:
            return self.__getattribute__('_' + key)
        else:
            return Canvas.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in kw:
            if key in self._widgetKeys:
                self[key] = kw[key]
                kw.pop(key, False)
        Canvas.config(self, **kw)

    def toggle(self):
        """Toggles the switch logical state"""
        self['boolean'] = not self._boolean

    def redraw(self):
        """Redraws the Logic Switch widget"""
        self.delete(self.lever)
        self.delete(self.back)
        for l in self.lines:
            self.delete(l)
        self._draw()

    def __draw_vertical(self, bfill, w, h):
        # lever coords
        if self._boolean:
            l = (1, 1, w - 1, h / 3 - 1)
            b = (1 * w / 4 + 1, h / 3 + 1, 3 * w / 4 - 1, h - 1)
        else:
            l = (1, 2 * h / 3 + 1, w - 1, h - 1)
            b = (1 * w / 4 + 1, 1, 3 * w / 4 - 1, 2 * h / 3 - 1)
        # drawing lever and background
        self.lever = self.create_rectangle(l[0], l[1], l[2], l[3], fill='#CCC')
        self.back = self.create_rectangle(b[0], b[1], b[2], b[3], fill=bfill)
        # drawing relief lines
        y0 = h / 9 if self._boolean else 7 * h / 9
        y1 = 2 * h / 9 if self._boolean else 8 * h / 9
        x_step = w / 5
        self.lines = []
        for x in [1, 2, 3, 4]:
            self.lines.append(self.create_line(x * x_step, y0, x * x_step, y1))

    def __draw_horizontal(self, bfill, w, h):
        # lever coords
        if self._boolean:
            l = (2 * w / 3 + 1, 1, w - 1, h - 1)
            b = (1, 1 * h / 4 + 1, 2 * w / 3 - 1, 3 * h / 4 - 1)
        else:
            l = (1, 1, w / 3 - 1, h - 1)
            b = (w / 3 + 1, 1 * h / 4 + 1, w - 1, 3 * h / 4 - 1)
        # drawing lever and background
        self.lever = self.create_rectangle(l[0], l[1], l[2], l[3], fill='#CCC')
        self.back = self.create_rectangle(b[0], b[1], b[2], b[3], fill=bfill)
        # drawing relief lines
        x0 = 7 * w / 9 if self._boolean else w / 9
        x1 = 8 * w / 9 if self._boolean else 2 * w / 9
        y_step = h / 5
        self.lines = []
        for y in [1, 2, 3, 4]:
            self.lines.append(self.create_line(x0, y * y_step, x1, y * y_step))

    def _draw(self):
        """Draws the Logic Switch widget"""
        w, h = int(self['width']), int(self['height'])
        bfill = self._coloron if self._boolean else self._coloroff
        if self._orientation == VERTICAL:
            self.__draw_vertical(bfill, w, h)
        else:
            self.__draw_horizontal(bfill, w, h)


if __name__ == '__main__':
    def toggle(evt):
        evt.widget.toggle()


    root = Tk()
    frame = Frame(root)
    for i in range(8):
        sw = LogicSwitch(frame, width=25, height=30)
        sw.pack(side=LEFT, fill=BOTH, expand=1)
        sw.bind('<Button-1>', toggle)
        if 4 <= i < 6:
            sw['coloroff'] = '#CCC'
            sw['coloron'] = '#00F'
    sw = LogicSwitch(frame, width=50, height=25, orientation=HORIZONTAL)
    sw.pack(side=LEFT, fill=BOTH, expand=1)
    sw.bind('<Button-1>', toggle)
    frame.pack(fill=BOTH, expand=1)
    root.mainloop()
