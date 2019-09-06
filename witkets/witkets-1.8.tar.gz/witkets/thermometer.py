#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *
from witkets.tank import Tank


class Thermometer(Tank):
    """A vertical-oriented widget for measuring temperature
        
       Options (all have default values):
          - colorlow, colormedium, colorhigh --- Colors for different levels
          - levellow --- Value below which the level is considered low
          - levelhigh --- Value above which the level is considered high
          - multicolor --- Whether to show level ranges with different colors
          - number --- Current value
          - numvariable --- Tk numeric variable to stock current value
          - tickfont --- Font for showing ticks
          - tickformat --- printf-like format to ticks
          - valformat --- printf-like format to value
          - minvalue --- Minimum value
          - maxvalue --- Maximum value
          - step --- Ticks step
          - hpad --- Horizontal padding (percentual)
          - All :code:`Canvas` widget options (notably width and height)
       
       If different colors are not desired, just set all three colors (low,
       medium and high) to the same value.
        
       Example:
          >>> from witkets import Thermometer
          >>> thermo = Thermometer(minvalue=32)
          >>> thermo['ystep'] = 5
          >>> thermo.config(number = 25)
    """

    def __init__(self, master=None, colorlow='blue', colormedium='green',
                 colorhigh='red', levellow=20, levelhigh=80, number=50,
                 numvariable=None, minvalue=0, maxvalue=100, step=10, hpad=0.2,
                 multicolor=False, tickfont='"Courier New" 6', tickformat='%d',
                 valformat='%.2f', **kw):
        # Default dimensions
        if 'width' not in kw:
            kw['width'] = 120
        if 'height' not in kw:
            kw['height'] = 200
        # Canvas related
        self._x1k = 0.2222
        self._x2k = 0.7777
        self._y1borderk = 0.7899
        self._y2borderk = 0.0340
        self._y1k = 0.75
        self._y2k = 0.0682
        self._x1tickK = 0.7222
        self._x2tickK = 0.8333
        self._xTextK = 0.8888
        Tank.__init__(self, master, colorlow=colorlow, colormedium=colormedium,
                      colorhigh=colorhigh, levellow=levellow,
                      levelhigh=levelhigh, number=number, vpad=0.0,
                      numvariable=numvariable, orientation=VERTICAL,
                      minvalue=minvalue, maxvalue=maxvalue, step=step,
                      hpad=hpad, multicolor=multicolor, tickfont=tickfont,
                      tickformat=tickformat, valformat=valformat, **kw)
        self._widget_keys.remove('orientation')
        self._widget_keys.remove('vpad')

    # =====================================================================
    # Coordinates conversion
    # =====================================================================

    def _yw2s(self, w):
        """Converts Y world coordinates to Y screen coordinates"""
        dw = self._maxvalue - self._minvalue
        ds = (self._y2k - self._y1k) * float(self._height)
        return (ds / dw) * (w - self._minvalue) + self._y1k * self._height

    def _ys2w(self, s):
        """Converts Y screen coordinates to Y world coordinates"""
        dw = float(self._maxvalue - self._minvalue)
        ds = (self._y2k - self._y1k) * float(self._height)
        return (dw / ds) * (s - self._y1k * self._height) + self._minvalue

    def _get_x(self, x):
        hpad = self._hpad * self._width
        return (self._width - 2 * hpad) * x + hpad

        # =====================================================================

    # Drawing functions
    # =====================================================================

    def _draw(self):
        """Draws the Thermometer widget"""
        w, h = self._width, self._height
        x1 = self._get_x(self._x1k)
        x2 = self._get_x(self._x2k)
        number = self._var.get()
        if number > self._maxvalue:
            number = self._maxvalue
        elif number < self._minvalue:
            number = self._minvalue
        self._draw_borders(h, x1, x2)
        self._draw_fluid(h, x1, x2, number)
        self._draw_ticks(number)

    def _draw_borders(self, h, x1, x2):
        self._arc = self.create_arc(self._get_x(0), 0.9772 * h,
                                    self._get_x(1), 0.7727 * h,
                                    style=CHORD, start=123, extent=292)
        y1 = self._y1borderk * h
        y2 = self._y2borderk * h
        line1 = self.create_line(x1, y1, x1, y2)
        line2 = self.create_line(x2, y1, x2, y2)
        line3 = self.create_line(x1, y2, x2, y2)
        self._objects.extend((self._arc, line1, line2, line3))

    def _draw_fluid(self, h, x1, x2, number):
        y = self._yw2s(number)
        y1border = self._y1borderk * h + 2
        low = self._yw2s(self._levellow)
        high = self._yw2s(self._levelhigh)
        if not self._multicolor:
            if number <= self._levellow:
                color = self._colorlow
            elif number <= self._levelhigh:
                color = self._colormedium
            else:
                color = self._colorhigh
            self.itemconfig(self._arc, fill=color)
            r = self.create_rectangle(x1 + 1, y1border,
                                      x2 - 1, y, fill=color, width=0)
            self._objects.append(r)
        else:
            # Low level
            self.itemconfig(self._arc, fill=self._colorlow)
            r = self.create_rectangle(x1 + 1, y1border,
                                      x2 - 1, y, fill=self._colorlow, width=0)
            self._objects.append(r)
            # Medium level
            if number > self._levellow:
                r = self.create_rectangle(x1 + 1, low,
                                          x2 - 1, y, fill=self._colormedium,
                                          width=0)
                self._objects.append(r)
            if number > self._levelhigh:
                r = self.create_rectangle(x1 + 1, high,
                                          x2 - 1, y, fill=self._colorhigh,
                                          width=0)
                self._objects.append(r)

    def _draw_ticks(self, number):
        val = self._minvalue
        x1tick = self._get_x(self._x1tickK)
        x2tick = self._get_x(self._x2tickK)
        x_text = self._get_x(self._xTextK) + 4
        while val <= self._maxvalue:
            y = self._yw2s(val)
            l = self.create_line(x1tick, y, x2tick, y)
            self._objects.append(l)
            txt = self._tickformat % val
            tick = self.create_text(x_text, y, anchor='w', text=txt,
                                    font=self._tickfont)
            self._objects.append(tick)
            val += self._step
        # Drawing left tick
        x1 = self._get_x(0.1923)
        x2 = self._get_x(0.2692)
        x_text = self._get_x(0.1538) - 4
        y = self._yw2s(number)
        txt = self._valformat % number
        l = self.create_line(x1, y, x2, y)
        tick = self.create_text(x_text, y, anchor='e', text=txt,
                                font=self._tickfont)
        self._objects.extend((l, tick))

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        Tank.__setitem__(self, key, val)

    def __getitem__(self, key):
        return Tank.__getitem__(self, key)


# =====================================================================
# Test script
# =====================================================================

if __name__ == '__main__':
    root = Tk()
    t = Thermometer(root)
    # t['numvariable'] = IntVar()  #uncomment if you want only integers
    t['multicolor'] = False
    t['tickfont'] = '"Courier New" 9'
    t['height'] = 370
    t['width'] = 160
    t['hpad'] = 0.4
    t['levellow'] = 20
    t['levelhigh'] = 80
    t['step'] = 10
    t['number'] = 50
    t['minvalue'] = 0
    t['maxvalue'] = 120
    t.enable_mouse()
    t.pack()
    root.mainloop()
