#!/usr/bin/env python3

import collections.abc as abc
import tkinter as tk
import tkinter.ttk as ttk
import witkets as wtk
from witkets.core import wtk_types 
from .plotstyle import LineStyle, PointStyle


class Plot(tk.Canvas):
    """2D Plot with support for multiple series.

        Options (all have default values):
          - xlimits --- Plot Window X limits (defaults to [-1,1])
          - ylimits --- Plot Window Y limits (defaults to [-1,1])
          - xlabels --- X axis labels (many configuration values, see below)
          - ylabels --- Y axis labels (many configuration values, see below)
          - autorange --- Autorange (single value or [xautorange, yautorange])
          - padding --- Padding outside the plot grid (top, right, bottom, left)
          - labelsmargin --- Margin for labels (single value or [xmargin,ymargin])
          - labelsformat --- printf-like format to labels (single or compound)
          - labelsfont --- The font used in tics (single or compound)
          - boxlinestyle --- Plot window box style (:code:`LineStyle`)
          - gridlinestyle --- Plot window grid line style (:code:`LineStyle`)
          - All :code:`Canvas` widget options

        **Adding Curves**

        Once constructed, the method :code:`add_plot()` may be called
        to add :code:`Plot.Series` instances.

        **Limits**

        The *xlimits* and *ylimits* parameters must be lists with the
        lower and upper bounds for the axes. Each one defaults to 
        (-1 , 1)
        
        These parameters are automatically changed when *autorange* is set. 
        Autorange can be slow, since it will force a search for 
        minimum and maximum values. It is either a boolean or 
        a tuple with separate configurations for the axes.

        **Labels**

        Labels can be specified in several ways. If not supplied, 
        *xlabels* and *ylabels* will INITIALLY be defined 
        so that the plot grid has 5 lines in each axis.
        
        1. Number of divisions
        Type: string
        Example: `code`:'/5': (divide plot window in 5 intervals)


        2. Fixed step in world coordinates
        Type: number
        Example: `code`:math.pi/2: (each interval at pi/2)


        3. Custom values
        Type: list
        Example: `code`:[(2, "a"), (3, "b"), (5, "a+b")]
        Another method is to completely customize labels, using the same
        parameters *xlabels* and *ylabels*. In this case, each one is a 
        list of pairs where the first element is the label location in 
        world coordinate and the second is the UTF-8 string to be 
        rendered in that location. The grid divison lines will also
        be rendered in those locations.

        For the first two modes, numeric labels are shown by default. 
        The format may be adjusted using the *labelsformat*, which 
        receives printf-like format strings or a pair of such strings, 
        in the case of separate formats for X and Y axes.

        Either way, the user must specify a margin from the plot box,
        by using the *labelsmargin* parameter. If one value is supplied, 
        it is used for both X and Y axes. Another option is to pass a 
        tuple with individual configurations for both axes. The margin
        is given in pixels.

        The label font is specified with *labelsfont*. It can be also
        be a tuple for separate configuration for X and Y axes.

        The *padding* controls the white space used to put the labels. 
        It should be overridden with a list of four integer values,
        corresponding to top, right, bottom and left padding in that
        order. The size is given in pixels.

        **Line Styles**

        The default linestyle for the box and the grid may be overridden
        by specifying *boxlinestyle* and *gridlinestyle*. which are 
        :code:`witkets.plot.LineStyle` instances.
    """

    # =====================================================================            
    # Introspection
    # =====================================================================

    widget_keys = {
        'xlimits': wtk_types.plotlimits, 
        'ylimits': wtk_types.plotlimits, 
        'xlabels': wtk_types.plotlabels, 
        'ylabels': wtk_types.plotlabels, 
        'autorange': wtk_types.plotboolconfig, 
        'labelsformat': wtk_types.plotstrconfig, 
        'padding': wtk_types.plotintconfig,
        'labelsmargin': wtk_types.plotintconfig, 
        'labelsfont': wtk_types.plotstrconfig,
        'boxlinestyle': LineStyle, 
        'gridlinestyle': LineStyle
    }

    parent_keys = {} # get type dict from wtk.core.attributes[tk.Canvas]

    def __init__(self, master=None, xlimits=None, ylimits=None, autorange=False,
                xlabels='/5', ylabels='/5', labelsformat='%.2f', 
                padding=None, labelsmargin=5, labelsfont='"Courier New" 9', 
                boxlinestyle=None, gridlinestyle=None, **kw):
        tk.Canvas.__init__(self, master, **kw)
        # Canvas Objects
        self._lines = []
        self._box = []
        self._texts = []
        # Default Values
        if not xlimits:
            xlimits = [-1, 1]
        if not ylimits:
            ylimits = [-1, 1]
        if not padding:
            padding = (20, 20, 40, 60)
        if not boxlinestyle:
            boxlinestyle = LineStyle(linewidth=2)
        if not gridlinestyle:
            gridlinestyle = LineStyle(linecolor='#CCC', dash=(5,3))
        # User options
        self._autorange = autorange
        self._xlimits = xlimits
        self._ylimits = ylimits
        self._xlabels = xlabels  # grid step X (world coords)
        self._ylabels = ylabels  # grid step Y (world coords)
        self._padding = padding
        self._boxlinestyle = boxlinestyle
        self._gridlinestyle = gridlinestyle
        self._labelsmargin = labelsmargin
        self._labelsfont = labelsfont
        self._labelsformat = labelsformat
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
        if key in self.widget_keys:
            self.__setattr__('_' + key, val)
            if key == 'xlimits' or key == 'ylimits':
                self._update_world_coordsys()
        else:
            tk.Canvas.__setitem__(self, key, val)
            if key == 'width' or key == 'height':
                self._update_plot_coordsys()

    def __getitem__(self, key):
        if key in self.widget_keys:
            return self.__getattribute__('_' + key)
        else:
            return tk.Canvas.__getitem__(self, key)

    def config(self, **kw):
        base_kw = {}
        for key, val in kw.items():
            if key in self.widget_keys:
                self.__setattr__('_' + key, val)
            else:
                base_kw[key] = kw[key]
        tk.Canvas.config(self, **base_kw)
        if 'width' in kw or 'height' in kw:
            self._update_plot_coordsys()
        if 'xlimits' in kw or 'ylimits' in kw:
            self._update_world_coordsys()
        self.redraw()

    # =====================================================================
    # Static Methods
    # =====================================================================

    @staticmethod
    def get_padding4(padding):
        if not isinstance(padding, abc.Sequence):
            return [padding]*4
        elif len(padding) == 2:
            return (padding[0], padding[1], padding[0], padding[1])
        return padding

    @staticmethod
    def get_config(axis, value):
        """Get configuration (shared value or separate values for each axis)"""
        if isinstance(value, abc.Sequence) and not isinstance(value, str):
            return value[axis]
        else:
            return value

    @staticmethod
    def get_config_xy(value):
        if isinstance(value, abc.Sequence) and not isinstance(value, str):
            return value
        else:
            return (value, value)

    # =====================================================================
    # Helper Methods
    # =====================================================================

    def _update_limits(self, xautorange, yautorange, serieslist):
        """Update limits (autorange)"""
        changed = False
        for s in serieslist:
            for xw, yw in s.data:
                if xautorange:
                    if xw < self._xlimits[0]:
                        changed = True
                        self._xlimits[0] = xw
                    elif xw > self._xlimits[1]:
                        changed = True
                        self._xlimits[1] = xw
                if yautorange:
                    if yw < self._ylimits[0]:
                        changed = True
                        self._ylimits[0] = yw
                    elif yw > self._ylimits[1]:
                        changed = True
                        self._ylimits[1] = yw
        return changed


    def _update_world_coordsys(self):
        """Update World Coordinate System when limits changes."""
        self.coordsys_world = wtk.CoordSys2D(
            self._xlimits[0], self._xlimits[1],
            self._ylimits[0], self._ylimits[1]
        )

    def _update_plot_coordsys(self):
        """Update Screen Coordinate System when widget dimensions changes."""
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        padt, padr, padb, padl = self.get_padding4(self._padding)
        self.coordsys_plot = wtk.CoordSys2D(
            x_min=padl, x_max=(w - padr),
            y_min=padt, y_max=(h - padb),
            y_inverted=True
        )
    
    # =====================================================================            
    # Drawing Methods
    # =====================================================================

    def _draw_grid(self):
        """Draw grids and ticks """
        # Delete existing entities
        for obj in self._lines + self._texts:
            self.delete(obj)
        self.delete(self._box)
        # Draw Tics (lines and text)
        tic_kwargs = self._gridlinestyle.to_line_kwargs()
        self._draw_tics(0, tic_kwargs)
        self._draw_tics(1, tic_kwargs)
        # Draw external box
        x0, y0 = self.coordsys_plot.from_ndc(0, 0)
        x1, y1 = self.coordsys_plot.from_ndc(1, 1)
        box_kwargs = self._boxlinestyle.to_rect_kwargs()
        self._box = self.create_rectangle(x0, y0, x1, y1, **box_kwargs)

    def _draw_tics(self, axis, kwargs):
        """Draw tics (lines and labels) for an axis."""
        # Preparing config
        if axis == 0:
            labels = self._xlabels
            limits = self._xlimits
        else:
            labels = self._ylabels
            limits = self._ylimits
        # Case 1 : Custom labels
        if isinstance(labels, abc.Sequence) and not isinstance(labels, str):
            for aw, label in labels:
                self._draw_line(axis, aw, kwargs)
                self._draw_text(axis, aw, label)
        else:
            # Case 2 : Division pattern (e.g.: '/5')
            if isinstance(labels, str):
                if labels.startswith('/'):
                    div = int(labels[1:])
                    step = (limits[1] - limits[0]) / div
                else:
                    step = float(labels)
            # Case 3 : Number in World space
            else:
                step = labels
            aw = limits[0] + step # CAUTION: abs. value, not delta!
            while aw <= limits[1]:
                self._draw_line(axis, aw, kwargs)
                self._draw_text(axis, aw)
                aw += step

    def _draw_line(self, axis, aw, properties):
        """Draw a line for a tic (grid division)."""
        # Normalizing and precondition
        if axis == 0:
            an = self.coordsys_world.xconv.to_ndc(aw)
        else:
            an = self.coordsys_world.yconv.to_ndc(aw)
        if an >= 1.0:
            return
        # Compute coords
        if axis == 0:
            x0 = x1 = self.coordsys_plot.xconv.from_ndc(an)
            y0 = self.coordsys_plot.yconv.from_ndc(0)
            y1 = self.coordsys_plot.yconv.from_ndc(1)
        else:
            y0 = y1 = self.coordsys_plot.yconv.from_ndc(an)
            x0 = self.coordsys_plot.xconv.from_ndc(0)
            x1 = self.coordsys_plot.xconv.from_ndc(1)
        # Add line to canvas
        l = self.create_line((x0, y0, x1, y1), properties)
        self._lines.append(l)

    def _draw_text(self, axis, aw, label=None):
        """Draw a label."""
        # Normalizing and precondition
        if axis == 0:
            an = self.coordsys_world.xconv.to_ndc(aw)
        else:
            an = self.coordsys_world.yconv.to_ndc(aw)
        if an <= 0:
            return
        padding4 = self.get_padding4(self._padding)
        padding = padding4[2] if axis == 0 else padding4[3]
        labelformat = self.get_config(axis, self._labelsformat)
        labelfont = self.get_config(axis, self._labelsfont)
        labelmargin = self.get_config(axis, self._labelsmargin)
        anchor = 'n' if axis == 0 else 'e'
        if axis == 0:
            xscr = self.coordsys_plot.xconv.from_ndc(an)
            yscr = self.coordsys_plot.yconv.from_ndc(0) + labelmargin
        else:
            xscr = padding - labelmargin
            yscr = self.coordsys_plot.yconv.from_ndc(an)
        txt = label if label else labelformat % aw
        tic = self.create_text(xscr, yscr, anchor=anchor, text=txt,
                                font=labelfont)
        self._texts.append(tic)

    def _draw_curve_line(self, xw1, yw1, xw2, yw2, curve):
        kwargs = curve.linestyle.to_line_kwargs()
        # Culling
        if not (self.coordsys_world.in_range(xw1, yw1) or
                self.coordsys_world.in_range(xw2, yw2)):
            return # line would not be visible
        xn1, yn1 = self.coordsys_world.to_ndc(xw1, yw1)
        xn2, yn2 = self.coordsys_world.to_ndc(xw2, yw2)
        # FIXME if one point is outside the plot window, get the
        # first point inside the plot window
        xscr1, yscr1 = self.coordsys_plot.from_ndc(xn1, yn1)
        xscr2, yscr2 = self.coordsys_plot.from_ndc(xn2, yn2)
        l = self.create_line(xscr1, yscr1, xscr2, yscr2, kwargs)
        curve.canvas_objects.append(l)


    def _draw_curve_point(self, xw, yw, curve):
        style = curve.pointstyle
        kwargs = style.to_oval_kwargs()
        r = style.pointsize
        if style.pointshape != 'circle':
            raise ValueError('Only "circle" allowed for now.')
        xn, yn = self.coordsys_world.to_ndc(xw, yw)
        xscr, yscr = self.coordsys_plot.from_ndc(xn, yn)
        c = self.create_oval(xscr-r, yscr-r, xscr+r, yscr+r, kwargs)
        curve.canvas_objects.append(c)

    def _draw_curves(self, curveslist):
        """Draw curves with lines or points."""
        for curve in curveslist:
            size = len(curve.data)
            for i in range(size):
                xw1, yw1 = curve.data[i]
                pt1_inrange = self.coordsys_world.in_range(xw1, yw1)
                if curve.linestyle and i < (size - 1):
                    xw2, yw2 = curve.data[i+1]
                    pt2_inrange = self.coordsys_world.in_range(xw2, yw2)
                    # Two points inside plot window
                    if pt1_inrange and pt2_inrange:
                        self._draw_curve_line(xw1, yw1, xw2, yw2, curve)
                    # One point inside plot window
                    elif pt1_inrange or pt2_inrange:
                        pass #CALCULATE INTERSECTION WITH PLOT WINDOW
                if curve.pointstyle and pt1_inrange:
                    self._draw_curve_point(xw1, yw1, curve)


    def _clear_plots(self):
        """Erase all curves from the plot window."""
        for s in self._series:
            s.clear(self)

        
    # =====================================================================
    # Public API
    # =====================================================================

    def clear(self):
        """Remove all curves from the plot and redraw."""
        self._clear_plots()
        self._series = []
        self.redraw()

    def redraw(self, *args):
        """Force a complete redraw (grid and curves)"""
        xautorange = self.get_config(0, self._autorange)
        yautorange = self.get_config(1, self._autorange)
        if xautorange or yautorange:
            changed = self._update_limits(xautorange, yautorange, self._series)
            if changed:
                self._update_world_coordsys()
        self._clear_plots()
        self._draw_grid()
        self._draw_curves(self._series)

    def add_plot(self, series, redraw_all=False):
        """Add a plot series."""
        self._series.append(series)
        xautorange = self.get_config(0, self._autorange)
        yautorange = self.get_config(1, self._autorange)
        if xautorange or yautorange:
            changed = self._update_limits(xautorange, yautorange, [series])
            if changed:
                self._update_world_coordsys()
                self._clear_plots()
                self._draw_grid()
        if redraw_all:
            self.redraw()
        else:
            self._draw_curves([series])


# =====================================================================
# Module Test
# =====================================================================

if __name__ == '__main__':
    from math import sin, cos, pi, tan, radians
    from .series import Series

    root = tk.Tk()
    root.title('Plot Example')
    plot1 = Plot(root, width=360, height=230)
    plot1.pack(side='left', padx=25)
    plot2 = Plot(root, width=400, height=230)
    plot2['xlimits'] = (0, 6.28)
    plot2['xlabels'] = [(pi/2, 'π/2'), (pi, 'π'), 
                        (3*pi/2, '3π/2'), (2*pi, '2π')]
    plot2.pack(side='left', padx=25)
    plot2['autorange'] = (False, True)
    curve1 = [(radians(x), 2*sin(radians(x))) for x in range(360)]
    style1 = LineStyle(linewidth=2, linecolor='#800')
    series1 = Series(data=curve1, linestyle=style1)
    curve2 = [(radians(16*x), 1.5*cos(radians(16*x))) for x in range(23)]
    style2 = PointStyle()
    series2 = Series(data=curve2, pointstyle=style2)
    plot2.add_plot(series1)
    plot2.add_plot(series2)

    TEST_PLOT = '''
    <root>
    <plot wid='plot3' width='360' height='230' 
        xlimits='(0, 100)' xlabels='/4' ylimits='(-3.14, 3.14)' 
        ylabels='(-3.14, -pi),(-1.57, -pi/2),(0, 0),(1.57, pi/2),(3.14, pi)'
        labelsfont='"Arial" 11' labelsformat='(%d, %s)' />
    <geometry><pack for='plot3' /></geometry>
    </root>
    '''
    frame =  ttk.Frame(root)
    frame.pack(side='left')
    builder = wtk.TkBuilder(frame)
    builder.build_from_string(TEST_PLOT)
    root.mainloop()
