from labelseg.dialog import Ui_Dialog
import PyQt5
from PyQt5.QtWidgets import QDialog


class PixelRangeDialog(QDialog):
    def __init__(self):
        super(PixelRangeDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def get_result(self):
        min_val = self.ui.spinBox_min.value()
        max_val = self.ui.spinBox_max.value()
        return min_val, max_val