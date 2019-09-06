#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *
from math import pi, sin, cos


# @TODO Remove border

class Spinner(Canvas):
    """Simple spinner for indicating long actions
        
       Options:
          - active --- Whether the spinner is active
          - All :code:`Canvas` widget options (notably width and height)

    """

    def __init__(self, master=None, active=False, **kw):
        self._widgetkeys = ('active',)
        self._active = active
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
        # Canvas objects and math-related
        self._circles = []
        self._currAngle = 0  # 0 to 7 ; 45 degree step
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
        self._redraw()

    def __getitem__(self, key):
        if key in self._widgetkeys:
            return self.__getattr__('_' + key)
        else:
            return Canvas.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in kw:
            if key in self._widgetkeys:
                self.__setattr__('_' + key, kw[key])
                kw.pop(key, False)
        Canvas.config(self, **kw)
        self._redraw()

    def _redraw(self):
        """Redraws the Spinner widget"""
        if self._circles:
            for c in self._circles:
                self.delete(c)
        self._draw()

    def _draw(self):
        xc, yc = self._width / 2, self._height / 2
        small_r = 0.1 * self._width
        big_r = self._width / 2 - small_r - 2
        f = self._currAngle * 25
        for i in range(8):
            x = xc + big_r * cos(pi / 4 * i)
            y = yc + big_r * sin(pi / 4 * i)
            r = (x - small_r, y - small_r, x + small_r, y + small_r)
            f = (f + 25) % 200
            color = '#' + hex(f)[2:] * 3
            self._circles.append(self.create_oval(fill=color, *r))
        self._currAngle += 1
        if self._active:
            self.after(80, self._draw)


if __name__ == '__main__':
    def toggle(evt):
        evt.widget.toggle()


    root = Tk()
    spinner = Spinner(root, width=100, height=100)
    # spinner = Spinner(root)
    spinner['active'] = True
    spinner.pack()
    root.mainloop()
