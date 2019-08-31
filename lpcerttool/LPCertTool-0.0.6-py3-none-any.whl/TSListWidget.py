from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5 import QtGui

class TSListWidget(QListWidget):
    def __init__(self):
        super().__init__()

    def Cliecked(self, item):
        pass

    def create(self, sourceArray):
        for source in sourceArray:
            item = QListWidgetItem(self)
            self.addItem(item)
            customItem = QCustomQWidget()
            customItem.createCustom(source)
            self.setItemWidget(item, customItem)

class QCustomQWidget (QWidget):
    def __init__(self):
        super().__init__()

    def createCustom(self, source):
        name = source["name"]
        state = source["state"]
        if state == 0:
            stateDescription = "未下载"
        elif state == 1:
            stateDescription = "已下载"
        nameLabel = QLabel(name)
        stateLabel = QLabel(stateDescription)
        hLayout = QHBoxLayout()
        hLayout.addWidget(nameLabel)
        hLayout.addWidget(stateLabel)
        self.setLayout(hLayout)
