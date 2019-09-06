from witkets.plot import Plot, LineStyle

class ScopeChannel:
    """Data to be plotted, as well as its corresponding style."""
    def __init__(self, scope, linestyle=None, data=None):
        if not linestyle:
            linestyle = LineStyle()
        if not data:
            data = []
        self._scope = scope
        self._linestyle = linestyle
        self._data = data
        self._canvas_tag = str(id(self))
        self.reconfigure()

    def reconfigure(self):
        offset = Plot.get_config_xy(self._scope['offset'])
        screen_step = Plot.get_config_xy(self._scope['screen_step'])
        world_step = Plot.get_config_xy(self._scope['world_step'])
        padding4 = self._scope._padding4 #FIXME [scope] expose as property?
        height = self._scope.canvas.winfo_reqheight()
        self._line_kwargs = self._linestyle.to_line_kwargs()
        scale = [s/w for (s, w) in zip(screen_step, world_step)]
        self._xw2s = lambda x : (scale[0] * (x - offset[0])) + padding4[3]
        self._yw2s = lambda y : height - padding4[2] - (scale[1] * (y - offset[1]))

    def _draw_segment(self, x1w, y1w, x2w, y2w):
        x1scr, x2scr = self._xw2s(x1w), self._xw2s(x2w)
        y1scr, y2scr = self._yw2s(y1w), self._yw2s(y2w)
        coords = (x1scr, y1scr, x2scr, y2scr)
        self._scope.canvas.create_line(*coords, 
                                        tags=(self._canvas_tag, 'plot'),
                                        **self._line_kwargs)


    def add_point(self, xw, yw):
        """Append a point to the Scope Channel."""
        last_point = self._data[-1] if self._data else None
        self._data.append((xw, yw))
        self._scope.on_new_point(xw, yw)
        if last_point:
            x1w, y1w = last_point
            self._draw_segment(x1w, y1w, xw, yw)

    def draw(self):
        """Draw everything (use after calling the clear() method)."""
        if len(self._data) < 2:
            return
        for i in range(len(self._data) - 1):
            x1w, y1w = self._data[i]
            x2w, y2w = self._data[i+1]
            self._draw_segment(x1w, y1w, x2w, y2w)

    def clear(self):
        """Delete all lines."""
        self._scope.canvas.delete(self._canvas_tag)
