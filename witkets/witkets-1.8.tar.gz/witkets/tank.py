#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *


class Tank(Canvas):
    """A gauge widget for measuring or setting level
        
       Options (all have default values):
          - colorlow, colormedium, colorhight --- Colors for different levels
          - levellow --- Value below which the level is considered low
          - levelhigh --- Value above which the level is considered high
          - multicolor --- Whether to show level ranges with different colors
          - number --- Current value
          - orientation --- Widget orientation (default is tk.VERTICAL)
          - numvariable --- Tk variable to stock current value
          - tickfont --- Font for showing ticks 
          - tickformat --- printf-like format to ticks
          - valformat --- printf-like format to value
          - hpad, vpad --- Widget padding (percentual)
          - minvalue --- Minimum value (in world units)
          - maxvalue --- Maximum value (in world units)
          - step --- Ticks step (in world units)
          - All :code:`Canvas` widget options (notably width and height)
       
       If different colors are not desired, just set all three colors (low,
       medium and high) to the same value.
        
       Example:
          >>> from witkets.Tank import Tank
          >>> tank = Tank(maxvalue=140)
          >>> tank['step'] = 50
          >>> tank.config(number = 25)
    """

    def __init__(self, master=None, colorlow='red', colormedium='blue',
                 colorhigh='green', hpad=0.2, levellow=20, levelhigh=80,
                 maxvalue=100, minvalue=0, multicolor=True, number=50,
                 numvariable=None, orientation=VERTICAL, step=20,
                 tickfont='"Courier New" 6', tickformat='%d', valformat='%.2f',
                 vpad=0.1, **kw):
        self._widget_keys = ['colorlow', 'colormedium', 'colorhigh',
                            'hpad', 'levellow', 'levelhigh', 'maxvalue',
                            'minvalue', 'multicolor', 'number', 'numvariable',
                            'orientation', 'step', 'tickfont', 'tickformat',
                            'vpad', 'valformat']
        if 'width' not in kw:
            kw['width'] = 110
        if 'height' not in kw:
            kw['height'] = 120
        if 'background' not in kw:
            kw['background'] = '#FFF'
        Canvas.__init__(self, master, **kw)
        if not numvariable:
            self._var = DoubleVar()
        else:
            self._var = numvariable
        self._var.set(number)
        self._var.trace('w', self._redraw)
        # Initializing default values
        self._colorlow = colorlow
        self._colormedium = colormedium
        self._colorhigh = colorhigh
        self._hpad = hpad
        self._vpad = vpad
        self._minvalue = minvalue
        self._maxvalue = maxvalue
        self._orientation = orientation
        self._step = step
        self._levellow = levellow
        self._levelhigh = levelhigh
        self._tickfont = tickfont
        self._multicolor = multicolor
        self._tickformat = tickformat
        self._valformat = valformat
        # Internal state
        self._motion = False
        self._height = int(kw['height'])
        self._width = int(kw['width'])
        # Canvas related
        self._objects = []
        self._draw()

    # =====================================================================
    # Coordinates conversion
    # =====================================================================

    def _yw2s(self, yw):
        """Converts Y world coordinates to Y screen coordinates"""
        dw = self._maxvalue - self._minvalue
        y1 = self._get_y(1)
        y2 = self._get_y(0)
        ds = (y2 - y1)
        return (ds / dw) * (yw - self._minvalue) + y1

    def _ys2w(self, ys):
        """Converts Y screen coordinates to Y world coordinates"""
        dw = float(self._maxvalue - self._minvalue)
        y1 = self._get_y(1)
        y2 = self._get_y(0)
        ds = (y2 - y1)
        return (dw / ds) * (ys - y1) + self._minvalue

    def _xw2s(self, xw):
        dw = self._maxvalue - self._minvalue
        x1 = self._get_x(0)
        x2 = self._get_x(1)
        ds = (x2 - x1)
        return (ds / dw) * (xw - self._minvalue) + x1

    def _xs2w(self, xs):
        dw = float(self._maxvalue - self._minvalue)
        x1 = self._get_x(0)
        x2 = self._get_x(1)
        ds = (x2 - x1)
        return (dw / ds) * (xs - x1) + self._minvalue

    def _get_x(self, xk):
        hpad = self._hpad * self._width
        return (self._width - 2 * hpad) * xk + hpad

    def _get_y(self, yk):
        vpad = self._vpad * self._height
        return (self._height - 2 * vpad) * yk + vpad

    # =====================================================================
    # Mouse related
    # =====================================================================

    def enable_mouse(self):
        """Enable mouse events"""
        self.bind('<ButtonPress>', self._on_clicked)
        self.bind('<Motion>', self._on_motion)
        self.bind('<ButtonRelease>', self._on_release)

    def disable_mouse(self):
        """Disables mouse events"""
        self.unbind('<ButtonPress>')
        self.unbind('<Motion>')
        self.unbind('<ButtonRelease>')

    def _on_clicked(self, event):
        """Mouse clicked callback"""
        xrel = event.x_root - event.widget.winfo_rootx()
        yrel = event.y_root - event.widget.winfo_rooty()
        new_level = self.screen2number(xrel, yrel)
        event.widget['number'] = new_level
        self._motion = True

    def _on_release(self, event):
        """Mouse button release callback"""
        self._motion = False

    def _on_motion(self, event):
        """Mouse motion callback"""
        if not self._motion:
            return
        xrel = event.x_root - event.widget.winfo_rootx()
        yrel = event.y_root - event.widget.winfo_rooty()
        new_level = self.screen2number(xrel, yrel)
        event.widget['number'] = new_level

    def screen2number(self, xscreen, yscreen):
        """Gets the level corresponding to a screen coordinate"""
        if self._orientation == VERTICAL:
            yscreen = yscreen if yscreen >= self._ymin_scr else self._ymin_scr
            yscreen = yscreen if yscreen <= self._ymax_scr else self._ymax_scr
            return self._ys2w(yscreen)
        else:
            xscreen = xscreen if xscreen >= self._xmin_scr else self._xmin_scr
            xscreen = xscreen if xscreen <= self._xmax_scr else self._xmax_scr
            return self._xs2w(xscreen)

    # =====================================================================
    # Drawing functions
    # =====================================================================

    def _reconfigure(self):
        """Reconfigures internal state"""
        self._height = int(self['height'])
        self._width = int(self['width'])
        self._ymin_scr = 0  # no padding!
        self._ymax_scr = self._height
        self._xmin_scr = 0
        self._xmax_scr = self._width

    def _redraw(self, *event):
        """Redraws the Tank widget"""
        for o in self._objects:
            self.delete(o)
        self._draw()

    def _draw(self):
        """Draws the Tank widget"""
        w, h = self._width, self._height
        number = self._var.get()
        if number > self._maxvalue:
            number = self._maxvalue
        elif number < self._minvalue:
            number = self._minvalue
        if self._orientation == VERTICAL:
            self._vdraw(w, h, number)
        else:
            self._hdraw(w, h, number)

    def _vdraw(self, w, h, number):
        x1 = self._get_x(0.15)
        x2 = self._get_x(0.85)
        r = self.create_rectangle(x1, self._get_y(0),
                                  x2, self._get_y(1))
        self._objects.append(r)
        self._vdrawfluid(x1, x2, number)
        self._vdrawticks(h)

    def _vdrawfluid(self, x1, x2, number):
        y_scr = self._yw2s(number)
        low = self._yw2s(self._levellow)
        high = self._yw2s(self._levelhigh)
        # Drawing fluid
        if not self._multicolor:
            if number <= self._levellow:
                color = self._colorlow
            elif number <= self._levelhigh:
                color = self._colormedium
            else:
                color = self._colorhigh
            r = self.create_rectangle(x1 + 1, self._get_y(1),
                                      x2 - 1, y_scr,
                                      fill=color, width=0)
            self._objects.append(r)
        else:
            # Low level
            r = self.create_rectangle(x1 + 1, self._get_y(1),
                                      x2 - 1, y_scr,
                                      fill=self._colorlow, width=0)
            self._objects.append(r)
            # Medium level
            if number > self._levellow:
                r = self.create_rectangle(x1 + 1, low,
                                          x2 - 1, y_scr,
                                          fill=self._colormedium, width=0)
                self._objects.append(r)
            if number > self._levelhigh:
                r = self.create_rectangle(x1 + 1, high,
                                          x2 - 1, y_scr,
                                          fill=self._colorhigh, width=0)
                self._objects.append(r)

    def _vdrawticks(self, number):
        val = self._minvalue
        x1tick = self._get_x(0.75)
        x2tick = self._get_x(0.95)
        x_text = self._get_x(1)
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
        x1 = self._get_x(0.05)
        x2 = self._get_x(0.25)
        x_text = self._get_x(0)
        y = self._yw2s(number)
        txt = self._valformat % number
        l = self.create_line(x1, y, x2, y)
        tick = self.create_text(x_text, y, anchor='e', text=txt,
                                font=self._tickfont)
        self._objects.extend((l, tick))

    def _hdraw(self, w, h, number):
        y2 = self._get_y(0.15)
        y1 = self._get_y(0.85)
        r = self.create_rectangle(self._get_x(0), y1,
                                  self._get_x(1), y2)
        self._objects.append(r)
        self._hdrawfluid(y1, y2, number)
        self._hdrawticks(h)

    def _hdrawfluid(self, y1, y2, number):
        x_scr = self._xw2s(number)
        low = self._xw2s(self._levellow)
        high = self._xw2s(self._levelhigh)
        # Drawing fluid
        if not self._multicolor:
            if number <= self._levellow:
                color = self._colorlow
            elif number <= self._levelhigh:
                color = self._colormedium
            else:
                color = self._colorhigh
            r = self.create_rectangle(self._get_x(0), y1 + 1,
                                      x_scr, y2 - 1,
                                      fill=color, width=0)
            self._objects.append(r)
        else:
            # Low level
            r = self.create_rectangle(self._get_x(0), y1 + 1,
                                      x_scr, y2 - 1,
                                      fill=self._colorlow, width=0)
            self._objects.append(r)
            # Medium level
            if number > self._levellow:
                r = self.create_rectangle(low, y1 + 1,
                                          x_scr, y2 - 1,
                                          fill=self._colormedium, width=0)
                self._objects.append(r)
            if number > self._levelhigh:
                r = self.create_rectangle(high, y1 + 1,
                                          x_scr, y2 - 1,
                                          fill=self._colorhigh, width=0)
                self._objects.append(r)

    def _hdrawticks(self, number):
        val = self._minvalue
        y1tick = self._get_y(0.7)
        y2tick = self._get_y(0.9)
        y_text = self._get_y(1) + 6
        while val <= self._maxvalue:
            x = self._xw2s(val)
            l = self.create_line(x, y1tick, x, y2tick)
            self._objects.append(l)
            txt = self._tickformat % val
            tick = self.create_text(x, y_text, anchor='c', text=txt,
                                    font=self._tickfont)
            self._objects.append(tick)
            val += self._step
        # Drawing left tick
        y1 = self._get_y(0.15)
        y2 = self._get_y(0.25)
        y_text = self._get_y(0) - 6
        x = self._xw2s(number)
        txt = self._valformat % number
        l = self.create_line(x, y1, x, y2)
        tick = self.create_text(x, y_text, anchor='c', text=txt,
                                font=self._tickfont)
        self._objects.extend((l, tick))

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key in self._widget_keys:
            if key == 'number':
                self._var.set(val)
            elif key == 'numvariable':
                self._var = val
                self._var.trace('w', self._redraw)
            else:
                self.__setattr__('_' + key, val)
        else:
            Canvas.__setitem__(self, key, val)
        self._reconfigure()
        self._redraw()

    def __getitem__(self, key):
        if key in self._widget_keys:
            if key == 'number':
                return self._var.get()
            elif key == 'numvariable':
                return self._var
            else:
                return self.__getattribute__('_' + key)
        else:
            return Canvas.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in kw:
            if key in self._widget_keys:
                if key == 'number':
                    self._var.set(kw[key])
                elif key == 'variable':
                    self._var = kw[key]
                    self._var.trace('w', self._redraw)
                else:
                    self[key] = kw[key]
                kw.pop(key, False)
        Canvas.config(self, **kw)
        self._reconfigure()
        self._redraw()


# =====================================================================            
# Test script
# =====================================================================

if __name__ == '__main__':
    root = Tk()
    t = Tank(root)
    # t['variable'] = IntVar()  #uncomment if you want only integers
    t['multicolor'] = False
    t['tickfont'] = '"Courier New" 10'
    t['height'] = 300
    t['width'] = 140
    t['hpad'] = 0.3
    t['vpad'] = 0.05
    t['levellow'] = 20
    t['levelhigh'] = 80
    t['step'] = 10
    t['number'] = 90.8
    t.enable_mouse()
    t.pack()
    t2 = Tank(root)
    # t['variable'] = IntVar()  #uncomment if you want only integers
    t2['multicolor'] = False
    t2['tickfont'] = '"Courier New" 10'
    t2['height'] = 140
    t2['width'] = 300
    t2['hpad'] = 0.05
    t2['vpad'] = 0.3
    t2['orientation'] = HORIZONTAL
    t2['levellow'] = 20
    t2['levelhigh'] = 80
    t2['step'] = 30
    t2['number'] = 90.8
    t2.enable_mouse()
    t2.pack()
    root.mainloop()
