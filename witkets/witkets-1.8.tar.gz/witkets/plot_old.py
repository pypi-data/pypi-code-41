#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
import witkets as wtk

class Plot(tk.Canvas):
    """Simple 2D Plot
       
        Options (all have default values):
          - xstep --- Grid horizontal step size in world coordinates
          - ystep --- Grid vertical step size in world coordinates
          - xrange --- Plot Window X limits (None for auto)
          - yrange --- Plot Window Y limits (None for auto)
          - padding --- Padding outside the plot grid
          - boxlinestyle --- Plot window box style
          - gridlinestyle -- Plot window grid line style
          - ticsfont --- The font used in tics (labels)
          - yticsformat --- printf-like format to Y tics
          - xticsformat --- printf-like format to X tics
          - All :code:`Canvas` widget options

        If not supplied, *xstep* and *ystep* will be defined so that 
        the plot grid has 5 lines in each axis.

        The *xlimits* and *ylimits* parameters must be lists with the
        lower and upper bounds for the axes. They should be set to 
        **None** if for autorange.

        The *padding* controls the white space used to put the labels. 
        It should be overridden with a list of four integer values,
        corresponding to top, right, bottom and left padding in that
        order.

        The default linestyle for the box and the grid may be overridden
        by specifying *boxlinestyle* and *gridlinestyle*. which are 
        :code:`Plot.LineStyle` instances.

        Once constructed, the method :code:`add_plot()` may be called
        to add :code:`Plot.Series` instances.
    """


    class LineStyle:
        """Line style for specifying width, color, etc ("dash")."""
        def __init__(self, linewidth=1, linecolor='#000', **kw):
            self.linewidth = linewidth
            self.linecolor = linecolor
            self.kw = {}
            for key in kw:
                self.kw[key] = kw[key]


    class PointStyle:
        """Point style for specifying size, color and shape."""
        def __init__(self, pointsize=3, pointcolor='#000', 
                     pointshape='circle'):
            self.pointsize = pointsize
            self.pointcolor = pointcolor
            self.pointshape = pointshape


    class Series:
        """Data to be plotted, as well as its corresponding style."""
        def __init__(self, linestyle=None, pointstyle=None):
            # At least one must be active
            if (not linestyle) and (not pointstyle):
                linestyle = Plot.LineStyle()
            self.linestyle = linestyle
            self.pointstyle = pointstyle
            self.data = []
            self.canvas_objects = []

        def set_data(self, points):
            """Set plot data."""
            self.data = points

    
    def __init__(self, master=None, xstep=None, ystep=None, padding=None,
                 xlimits=None, ylimits=None, xticsformat='%.2f ',
                 yticsformat='%.2f ', boxlinestyle=None, ticslinestyle=None, 
                 ticsfont='"Courier New" 9', **kw):
        self._plotkeys = {
            'xstep': float, 'ystep': float, 'padding': list, 'xrange': list,
            'yrange': list, 'boxlinestyle': str, 'ticslinestyle': str, 
            'ticsfont': str, 'xticsformat': str, 'yticsformat': str
        }
        tk.Canvas.__init__(self, master, **kw)
        # Canvas Objects
        self._vlines = []
        self._hlines = []
        self._box = []
        self._texts = []
        # Default Values
        if not xlimits:
            xlimits = (-1, 1)
        if not ylimits:
            ylimits = (-1, 1)
        if not xstep:
            xstep = (xlimits[1] - xlimits[0]) / 5
        if not ystep:
            ystep = (ylimits[1] - ylimits[0]) / 5
        if not padding:
            padding = (20, 20, 40, 60)
        if not boxlinestyle:
            boxlinestyle = self.LineStyle(linewidth=2)
        if not ticslinestyle:
            ticslinestyle = self.LineStyle(linecolor='#CCC', dash=(5,3))
        # User options
        self._xstep = xstep  # grid step X (world coords)
        self._ystep = ystep  # grid step Y (world coords)
        self._xlimits = xlimits
        self._ylimits = ylimits
        self._padding = padding
        self._boxlinestyle = boxlinestyle
        self._ticslinestyle = ticslinestyle
        self._ticsfont = ticsfont
        self._xticsformat = xticsformat
        self._yticsformat = yticsformat
        # Plot state
        self._series = []
        # Initial config
        self._update_plot_coordsys()
        self._update_world_coordsys()
        if 'background' not in kw:
            self['background'] = '#FFF'
        self.redraw()

    # =====================================================================            
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key in self._plotkeys:
            val = self._plotkeys[key](val)
            self.__setattr__('_' + key, val)
            if key == 'xlimits' or key == 'ylimits':
                self._update_world_coordsys()
            self.redraw()
        else:
            tk.Canvas.__setitem__(self, key, val)
            self._update_plot_coordsys()

    def __getitem__(self, key):
        if key in self._plotkeys:
            return self.__getattribute__('_' + key)
        else:
            return tk.Canvas.__getitem__(self, key)

    def config(self, **kw):
        base_kw = {}
        for key, val in kw.items():
            if key in self._plotkeys:
                self.__setattr__('_' + key, val)
                if key == 'xlimits' or key == 'ylimits':
                    self._update_world_coordsys()
            else:
                base_kw[key] = kw[key]
        tk.Canvas.config(self, **base_kw)
        self.redraw()

    # =====================================================================            
    # Drawing Methods
    # =====================================================================

    def _draw_grid(self):
        """Draw grids and ticks """
        # Delete existing entities
        for obj in self._vlines + self._hlines + self._texts:
            self.delete(obj)
        self.delete(self._box)
        # Draw external box
        x0, y0 = self.coordsys_plot.from_ndc(0, 0)
        x1, y1 = self.coordsys_plot.from_ndc(1, 1)
        kwargs = {
            'outline': self._boxlinestyle.linecolor,
            'width': self._boxlinestyle.linewidth
        }
        kwargs.update(self._boxlinestyle.kw)
        self._box = self.create_rectangle(x0, y0, x1, y1, **kwargs)
        # Draw tics
        # CAUTION: cannot convert DELTAs, only abs. coordinates
        xn, yn = self.coordsys_world.to_ndc(
            self._xstep + self._xlimits[0], 
            self._ystep + self._ylimits[0]
        )
        x, y = xn, yn
        kwargs = {
            'fill': self._ticslinestyle.linecolor,
            'width': self._ticslinestyle.linewidth
        }
        kwargs.update(self._ticslinestyle.kw)
        while x <= 1.0:
            x0, y0 = self.coordsys_plot.from_ndc(x, 0)
            x1, y1 = self.coordsys_plot.from_ndc(x, 1)
            if x < 1.0:
                l = self.create_line((x0, y0, x1, y1), **kwargs)
                self._vlines.append(l)
            # Text
            xw = self.coordsys_world.from_ndc(x, 0)[0]
            yscr = self.coordsys_plot.from_ndc(0, 0)[1]
            txt = self._xticsformat % xw
            tic = self.create_text(x0, yscr, anchor='n', text=txt,
                                   font=self._ticsfont)
            self._texts.append(tic)
            x += xn
        while y <= 1.0:
            x0, y0 = self.coordsys_plot.from_ndc(0, y)
            x1, y1 = self.coordsys_plot.from_ndc(1, y)
            if y < 1.0:
                l = self.create_line((x0, y0, x1, y1), **kwargs)
                self._hlines.append(l)
            # Text
            yw = self.coordsys_world.from_ndc(0, y)[1]
            txt = self._yticsformat % yw
            tic = self.create_text(self._padding[3], y0, anchor='e', text=txt,
                                   font=self._ticsfont)
            self._texts.append(tic)
            # TODO
            y += yn

        '''# Horizontal lines and Y ticks
        y = self._ymax_scr
        while y >= self._padt:
            l = self.create_line(self._padl, y, self._xmax_scr, y,
                                 fill=self._colorgrid)
            self._hlines_obj.append(l)
            if y != self._ymax_scr:
                tick_y = self._ys2w(y)
                txt = str(int(round(tick_y)))
                tick = self.create_text(self._padl - 2, y, anchor='e', text=txt,
                                        font=self._tickfont)
                self._ticks_obj.append(tick)
                if self._autoscroll and self._xmax_scr > (self.w + self._padl):
                    x = self._xmax_scr - self.w + self._padl + self._padr
                    
            y -= self._ystep * self._yscale'''

    def _draw_curves(self):
        pass

    def _update_world_coordsys(self):
        self.coordsys_world = wtk.CoordSys2D(
            *self._xlimits,
            *self._ylimits
        )

    def _update_plot_coordsys(self):
        w = int(self['width'])  # width
        h = int(self['height'])  # height
        padt, padr, padb, padl = self._padding
        self.coordsys_plot = wtk.CoordSys2D(
            x_min=padl, x_max=(w - padr),
            y_min=padt, y_max=(h - padb),
            y_inverted=True
        )
        
    def _clear_plots(self):
        for s in self._series:
            self.delete([obj for obj in s.canvas_objects])

    # =====================================================================
    # Public API
    # =====================================================================

    def clear(self):
        """Clear the plot"""
        self._clear_plots()
        self._series = []
        self.redraw()

    def redraw(self, *args):
        """Force a complete redraw (grid and curves)"""
        self._draw_grid()
        self._clear_plots()
        self._draw_curves()

    def add_plot(self, series):
        self._series.append(series)
        self.redraw()


# =====================================================================
# Module Test
# =====================================================================

if __name__ == '__main__':
    from math import sin, pi, tan

    root = tk.Tk()
    plot = Plot(root, width=360, height=230)
    plot.pack()
    root.mainloop()
