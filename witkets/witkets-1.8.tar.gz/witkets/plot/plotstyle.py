class LineStyle:
    """Line style for specifying width, color, etc ("dash")."""
    def __init__(self, linewidth=1, linecolor='#000', **kw):
        self.linewidth = linewidth
        self.linecolor = linecolor
        self.kw = {}
        for key in kw:
            self.kw[key] = kw[key]

    def to_line_kwargs(self):
        kwargs = {
            'fill': self.linecolor,
            'width': self.linewidth
        }
        kwargs.update(self.kw)
        return kwargs

    def to_rect_kwargs(self):
        kwargs = {
            'outline': self.linecolor,
            'width': self.linewidth
        }
        kwargs.update(self.kw)
        return kwargs


class PointStyle:
    """Point style for specifying size, color and shape."""
    def __init__(self, pointsize=2, pointcolor='#000', 
                    pointshape='circle', **kw):
        self.pointsize = pointsize
        self.pointcolor = pointcolor
        self.pointshape = pointshape
        self.kw = {}
        for key in kw:
            self.kw[key] = kw[key]

    def to_oval_kwargs(self):
        kwargs = { 'fill': self.pointcolor }
        kwargs.update(self.kw)
        return kwargs