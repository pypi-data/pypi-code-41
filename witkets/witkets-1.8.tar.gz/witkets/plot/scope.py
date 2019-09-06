#!/usr/bin/env python3

from collections import abc
import tkinter as tk
import tkinter.ttk as ttk
from .plotstyle import LineStyle
from .plot import Plot
from witkets.core import wtk_types 

class Scope(ttk.Frame):
    """Multi-channel Signal Scope
       
       Real-time plot with scrollbars.
       
       Options:
         - plot_width, plot_height --- Plot dimensions
         - screen_step --- Grid divison in pixels
         - world_step --- Grid division in world coordinates (X,Y)
         - offset --- Offset in world coordinates (X,Y)
         - autoscroll --- Autoscroll to last point
         - padding --- Padding outside the plot grid (top, right, bottom, left)
         - labelsmargin --- Margin for labels (single value or [xmargin,ymargin])
         - labelsformat --- printf-like format to labels (single or compound)
         - labelsfont --- The font used in tics (single or compound)
         - gridlinestyle --- Plot window grid line style (:code:`Plot.LineStyle`)
         - plot_* --- Pass other options to Canvas
         - All :code:`Frame` widget options
       
       Attributes:
         - canvas --- The associated :code:`tk.Canvas` object
         - hscroll and vscroll --- Scrollbar objects
    """
    # =====================================================================            
    # Introspection
    # =====================================================================

    widget_keys = {
        'plot_width': int, 
        'plot_height': int,
        'screen_step': wtk_types.plotintconfig,
        'world_step': wtk_types.plotrealconfig,
        'offset': wtk_types.plotrealconfig,
        'autoscroll': wtk_types.boolean,
        'padding': wtk_types.plotintconfig,
        'labelsformat': wtk_types.plotstrconfig,
        'labelsmargin': wtk_types.plotintconfig,
        'labelsfont': wtk_types.plotstrconfig,
        'gridlinestyle': LineStyle
    }

    def __init__(self, master=None, plot_width=330, plot_height=220, 
                 screen_step=40, world_step=0.1, offset=0, autoscroll=True,
                 highlightlast=False, padding=None, labelsformat='%.2f', 
                 labelsmargin=8, labelsfont='"Courier New" 9', 
                 gridlinestyle=None, **kw):
        plot_keys = {}
        for key in kw:
            if key.startswith('plot_'):
                plotkey = key.replace('plot_', '')
                plot_keys[plotkey] = kw[plotkey]
                kw.pop(key, False)
        ttk.Frame.__init__(self, master, **kw)
        self.canvas = tk.Canvas(self, width=plot_width, height=plot_height, 
                                **plot_keys)
        if 'plot_background' not in kw:
            self.canvas['background'] = '#FFF'
        self._style = None  # style attribute isn't stored properly
        # Properties initial values
        if not padding:
            padding = (20, 20, 40, 60)
        if not gridlinestyle:
            gridlinestyle = LineStyle(linecolor='#CCC', dash=(5,3))
        self._screen_step = screen_step
        self._world_step = world_step
        self._offset = offset
        self._padding = padding
        self._gridlinestyle = gridlinestyle
        self._autoscroll = autoscroll
        self._highlightlast = highlightlast
        self._labelsformat = labelsformat
        self._labelsmargin = labelsmargin
        self._labelsfont = labelsfont
        # Plot and scrollbars
        self.hscroll = ttk.Scrollbar(self, orient='horizontal')
        self.hscroll.config(command=self.canvas.xview)
        self.vscroll = ttk.Scrollbar(self, orient='vertical')
        self.vscroll.config(command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hscroll.set)
        self.canvas.config(yscrollcommand=self.vscroll.set)
        self.vscroll.grid(row=0, column=0, sticky='ns')
        self.canvas.grid(row=0, column=1, sticky='nsew')
        self.hscroll.grid(row=1, column=1, sticky='we')
        # Mouse-wheel zoom and pan
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)
        # Scope signals
        self._styles = []
        self._channels = []
        # State
        self._padding4 = Plot.get_padding4(self._padding)
        self._max_xw = None         # maximum X coord in world space
        self._last_grid_x = None    # last X tic a (screen, world) tuple
        # Drawing flags
        self._enable_redraw_lines = True    # redraw all grid lines next time
        self._enable_redraw_texts = True    # redraw all texts next time
        self._enable_redraw_plots = False   # redraw all plots next time
        self._lines_kwargs = None           # shortcut for line kwargs
        # Canvas objects
        self._grid_objects = []
        self.redraw()

    # =====================================================================            
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key.startswith('plot_'):
            plotkey = key.replace('plot_', '')
            self.canvas[plotkey] = val
        elif key == 'style':
            self._style = val
            ttk.Frame.__setitem__(self, 'style', val)
        elif key in self.widget_keys:
            self.__setattr__('_' + key, val)
        else:
            ttk.Frame.__setitem__(self, key, val)
        # FIXME : redraw only what's necessary.
        self._enable_redraw_lines = True
        self._enable_redraw_texts = True
        self._enable_redraw_plots = True
        self.redraw()

    def __getitem__(self, key):
        if key.startswith('plot_'):
            plotkey = key.replace('plot_', '')
            return self.canvas[plotkey]
        elif key in self.widget_keys:
            return self.__getattribute__('_' + key)
        elif key == 'style':
            return self._style
        else:
            ttk.Frame.__getitem__(self, key)

    def config(self, **kw):
        """Tk standard config method"""
        base_kw = {}
        for key, val in kw.items():
            if key.startswith('plot_'):
                plotkey = key.replace('plot_', '')
                self.canvas[plotkey] = kw[key]
            elif key in self.widget_keys:
                self.__setattr__('_' + key, val)
            else:
                base_kw[key] = kw[key]
        ttk.Frame.config(self, **base_kw)
        # FIXME : redraw only what's necessary.
        self._enable_redraw_lines = True
        self._enable_redraw_texts = True
        self._enable_redraw_plots = True
        self.redraw()

    # =====================================================================
    # Iterators
    # =====================================================================

    class TicsIterator:
        """Tics iterator for (screen, world) tuples.
            scope --- The scope object
            axis --- Axis Index (X=0, Y=1)
            start --- (screen, world) start point

            For X axis::

                |--|--|--|--|--|--|--|--|--|
                |--|--|--|--|--|--|--|--|--|
                |--|--|--|--|--|--|--|--|--|
                1  2  3      ...           n

            For Y axis::

                n--|--|--|--|--|--|--|--|--|--|
                 --|--|--|--|--|--|--|--|--|--|
                3--|--|--|--|--|--|--|--|--|--|
                2--|--|--|--|--|--|--|--|--|--|
                1--|--|--|--|--|--|--|--|--|--|
        """
        def __init__(self, scope, axis=0, start=None):
            self._scope = scope
            self._axis = axis
            self._screen_step = Plot.get_config(axis, self._scope._screen_step)
            self._world_step = Plot.get_config(axis, self._scope._world_step)
            self._padding4 = self._scope._padding4
            self._canvas_w = self._scope.canvas.winfo_reqwidth()
            self._canvas_h = self._scope.canvas.winfo_reqheight()
            if not start:
                if axis == 0:
                    self._screen = self._padding4[3] # pad left
                else:
                    self._screen = self._canvas_h - self._padding4[2] #pad b
                self._world = Plot.get_config(axis, self._scope._offset) 
            else:
                self._screen, self._world = start

        def __iter__(self):
            self.last = None
            if self._axis == 0:
                self._screen_stop = self._canvas_w - self._padding4[1] #pad r
            return self

        def __next__(self):
            """Next (screen, world) tuple"""
            screen = self._screen
            world = self._world
            # X axis: tics until width or last X
            if self._axis == 0:
                if self._scope._max_xw:
                    if world > self._scope._max_xw:
                        raise StopIteration()
                elif screen > self._screen_stop:
                    raise StopIteration()
                self._screen += self._screen_step
            # Y axis: tics until padding top
            else:
                if screen < self._padding4[0]:
                    raise StopIteration()
                self._screen -= self._screen_step
            self._world += self._world_step
            self.last = (screen, world)
            return self.last

    # =====================================================================
    # Helper Methods
    # =====================================================================            
    def zoom(self, axis, factor=1.2):
        self._world_step = Plot.get_config_xy(self._world_step)
        if axis == 0 or axis == 2:
            self._world_step[0] *= factor
        if axis == 1 or axis == 2:
            self._world_step[1] *= factor
        self._enable_redraw_lines = True
        self._enable_redraw_texts = True
        self._enable_redraw_plots = True
        self.redraw()

    def pan(self, axis, amount=10):
        self._offset = Plot.get_config_xy(self._offset)
        if axis == 0 or axis == 2:
            self._offset[0] += amount
        if axis == 1 or axis == 2:
            self._offset[1] += amount
        self._enable_redraw_texts = True
        self._enable_redraw_plots = True
        self.redraw()

    # =====================================================================
    # Drawing Methods
    # =====================================================================

    def _draw_grid_line(self, x1, y1, x2, y2, tags='grid'):
        self.canvas.create_line(x1, y1, x2, y2, tags=tags, **self._lines_kwargs)

    def _draw_grid_text(self, x, y, text, anchor, font, tags='grid'):
        """Draw a label at (x, y) position."""
        self.canvas.create_text(x, y, text=text, anchor=anchor, font=font, 
                                tags=tags)

    def _draw_grid(self):
        """Draw grid lines and texts (tics and labels)."""
        self._lines_kwargs = self._gridlinestyle.to_line_kwargs()
        xiter = self.TicsIterator(self, axis=0)
        yiter = self.TicsIterator(self, axis=1)
        # X axis
        y1 = self._padding4[0] # pad top
        y2 = self.canvas.winfo_reqheight() - self._padding4[2] # pad bottom
        if self._enable_redraw_texts:
            margins = Plot.get_config_xy(self._labelsmargin)
            formats = Plot.get_config_xy(self._labelsformat)
            fonts = Plot.get_config_xy(self._labelsfont)
        for (xs, xw) in xiter:
            if self._enable_redraw_lines:
                self._draw_grid_line(xs, y1, xs, y2, tags=('grid', 'x', 'line'))
            if self._enable_redraw_texts:
                txt = formats[0] % xw
                y = y2 + margins[0]
                tags = ('grid', 'y', 'text')
                self._draw_grid_text(xs, y, txt, 'n', fonts[0], tags=tags)
        # Y axis
        x1 = self._padding4[3]
        x2 = xiter.last[0]
        for (ys, yw) in yiter:
            if self._enable_redraw_lines:
                self._draw_grid_line(x1, ys, x2, ys, tags=('grid', 'y', 'line'))
            if self._enable_redraw_texts:
                txt = formats[1] % yw
                x = x1 - margins[1]
                tags = ('grid', 'x', 'text')
                self._draw_grid_text(x, ys, txt, 'e', fonts[1], tags=tags)
        self._enable_redraw_lines = False
        self._enable_redraw_texts = False
        self._last_grid_x = xiter.last

    def _update_grid_lines(self):
        """Update grid lines upon new data."""
        extents = self.canvas.bbox("all")
        # Update Y tics
        lines = self.canvas.find_withtag('line')
        ytics = [obj for obj in self.canvas.find_withtag('y') if obj in lines]
        for line in ytics:
            old_coords = self.canvas.coords(line)
            # ONLY 2 VALUES RETURNED :/
            x0, y0 = old_coords[0], old_coords[1]
            y1 = old_coords[3]
            x1 = extents[2]
            self.canvas.coords(line, x0, y0, x1, y1)
        # Add X tics
        self._lines_kwargs = self._gridlinestyle.to_line_kwargs()
        xiter = self.TicsIterator(self, axis=0, start=self._last_grid_x)
        y1 = self._padding4[0] # pad top
        y2 = self.canvas.winfo_reqheight() - self._padding4[2] # pad bottom
        margin = Plot.get_config(0, self._labelsmargin)
        labelformat = Plot.get_config(0, self._labelsformat)
        font = Plot.get_config(0, self._labelsfont)
        first = True
        for (xs, xw) in xiter:
            if first:
                first = False
                continue
            self._draw_grid_line(xs, y1, xs, y2, tags=('grid', 'x', 'line'))
            txt = labelformat % xw
            y = y2 + margin
            tags = ('grid', 'y', 'text')
            self._draw_grid_text(xs, y, txt, 'n', font, tags=tags)
        self._last_grid_x = xiter.last

    def _update_canvas_size(self):
        extents = list(self.canvas.bbox("plot"))
        extents[0] = 0
        extents[1] = 0
        extents[2] += self._padding4[1] # right padding
        extents[3] += self._padding4[2] # bottom padding
        self.canvas.configure(scrollregion=extents)

    # =====================================================================
    # Public API
    # =====================================================================

    def redraw(self):
        self._padding4 = Plot.get_padding4(self._padding)
        tags = []
        if self._enable_redraw_lines:
            tags.append('line')
        if self._enable_redraw_texts:
            tags.append('text')
        for t in tags:
            self.canvas.delete(t)
        self._last_grid_x = None
        self._draw_grid()
        # redraw plots?

    def on_new_point(self, xw, yw):
        """Called by a ScopeChannel instance to update scope grid bounds."""
        if not self._max_xw:
            self._max_xw = xw
        elif xw > self._max_xw:
            self._max_xw = xw
            self._update_grid_lines()
            self._update_canvas_size()
            if self._autoscroll:
                self.canvas.xview_moveto(1)

    # =====================================================================
    # Default Events
    # =====================================================================

    def _on_mouse_wheel(self, event):
        """Mouse wheel events"""
        shift = event.state & 1
        control = event.state & 4
        alt = event.state & 8
        # FIXME : show event values!! use key modifiers properly
        # 'delta', 'height', 'keycode', 'keysym', 'keysym_num', 'num',
        # 'send_event', 'serial', 'state', 'time', 'type', 'widget', 'width',
        # 'x', 'x_root', 'y', 'y_root'
        if event.delta != 0:  # Windows
            pass
        elif event.num == 4:  # Linux
            if control and (not shift) and (not alt):
                self.zoom(axis=2, factor=1.2)
            elif shift and (not control) and (not alt):
                self.canvas.xview('scroll', -1, 'units')
            elif alt and (not control) and (not shift):
                self.pan(axis=1, amount=-10)
            elif control and shift and (not alt):
                self.zoom(axis=1, factor=1.2)
            else:
                self.canvas.yview('scroll', -1, 'units')
        elif event.num == 5:
            if control and (not shift) and (not alt):
                self.zoom(axis=2, factor=1.2)
            elif shift and (not control) and (not alt):
                self.canvas.xview('scroll', 1, 'units')
            elif alt and (not control) and (not shift):
                self.pan(axis=1, amount=10)
            elif control and shift and (not alt):
                self.zoom(axis=2, factor=1/1.2)
            else:
                self.canvas.yview('scroll', 1, 'units')


if __name__ == '__main__':
    import math
    from witkets.plot import ScopeChannel
    
    angle = 0
    
    def new_point():
        global angle
        x = math.radians(angle)
        y = math.sin(x)
        channel.add_point(x, y)
        angle += 10
        root.after(100, new_point)

    def reconfigure_test():
        scope['plot_width'] = 1500

    root = tk.Tk()
    scope = Scope(root, plot_width=480, plot_height=480)
    scope.config(padding=[40, 40, 40, 40], world_step=[0.8, 0.2], 
                 offset=[-3, -1])
    channel = ScopeChannel(scope)
    root.after(30, new_point)
    root.after(1500, reconfigure_test)
    scope.pack()
    root.mainloop()
