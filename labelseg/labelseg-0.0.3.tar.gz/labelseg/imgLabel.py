from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QMouseEvent

class ImgLabel(QLabel):
    mouse_pressed = pyqtSignal(QMouseEvent)
    mouse_move = pyqtSignal(QMouseEvent)
    mouse_release = pyqtSignal(QMouseEvent)

    def __init__(self, parent):
        super(ImgLabel, self).__init__(parent)

    def mousePressEvent(self, ev):
        self.mouse_pressed.emit(ev)

    def mouseMoveEvent(self, ev):
        self.mouse_move.emit(ev)

    def mouseReleaseEvent(self, ev):
        self.mouse_release.emit(ev)