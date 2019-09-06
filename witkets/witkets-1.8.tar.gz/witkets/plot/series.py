from .plotstyle import LineStyle

class Series:
    """Data to be plotted, as well as its corresponding style."""
    def __init__(self, linestyle=None, pointstyle=None, data=None):
        # At least one must be active
        if (not linestyle) and (not pointstyle):
            linestyle = LineStyle()
        self.linestyle = linestyle
        self.pointstyle = pointstyle
        if not data:
            data = []
        self.data = data
        self.canvas_objects = []

    def clear(self, canvas):
        for obj in self.canvas_objects:
            canvas.delete(obj)