import sys
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy, QTextEdit
from matplotlib.figure import Figure
from functions import Residual

class MplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = fig
        # self.axes = fig.add_subplot(111)

        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass
    
class DrawResidual:
    def __init__(self,fig,filename):
        self.axes = fig.add_subplot(111)
        
        self.set_residual_file(filename)
    def set_residual_file(filename):
        self.res = Residual(filename)
        self.filename = filename
        
class SongziShell(QTextEdit):
    pass