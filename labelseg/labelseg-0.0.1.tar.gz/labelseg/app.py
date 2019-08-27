import sys
import PyQt5
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QFileDialog, QMessageBox, QColorDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QColor
from labelseg.mainwindow import Ui_MainWindow
import cv2 as cv
from enum import Enum
import os
from pathlib import Path
import labelseg.util as util
from PyQt5.Qt import QMouseEvent
from labelseg.app_dialog import PixelRangeDialog
import logging
import numpy as np


class OPEN_MODE(Enum):
    OPEN_FILE = 1
    OPEN_DIR = 2


class STATE(Enum):
    NORMAL = 1
    DRAW_POLYGON = 2


class AppWindow(QMainWindow):
    def __init__(self):
        super(AppWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.img_area.setScaledContents(False)
        self.ui.img_area.setStyleSheet('border: 1px solid red')
        self.add_tool_bar()
        self.bind_actions()
        self.init_vars()

    def init_vars(self):
        self.open_mode = OPEN_MODE.OPEN_FILE
        self.opened_files = []
        self.cur_img = None
        self.panel_pic = None  # 用来在上面绘制矩阵等形状
        self.origin_img = None  # 保留原始大小的图片
        self.labelimg = None
        self.scale = 1
        self.cur_rect_list = []
        self.cur_label_list = []
        self.histroty = []
        self.fill_color = QColor('green')
        self.pixel_range = [-5, 5]
        self.state = STATE.NORMAL
        self.start_point = None
        self.end_point = None
        self.modified = False
        self.saved = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s %(funcName)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def refresh_vars(self):
        self.cur_img = None
        self.panel_pic = None  # 用来在上面绘制矩阵等形状
        self.origin_img = None  # 保留原始大小的图片
        self.labelimg = None
        self.scale = 1
        self.cur_rect_list = []
        self.cur_label_list = []
        self.histroty = []
        self.state = STATE.NORMAL
        self.ui.actionCreate_Polygon.setChecked(False)
        self.start_point = None
        self.end_point = None
        self.modified = False
        self.saved = False

    def bind_actions(self):
        self.ui.actionOpen_File.triggered.connect(self.open_file)
        self.ui.actionOpen_Dir.triggered.connect(self.open_dir)
        self.ui.file_list.itemClicked.connect(self.file_list_item_changed)
        self.ui.actionZoom_In.triggered.connect(self.zoom_in_pic)
        self.ui.actionZoom_Out.triggered.connect(self.zoom_out_pic)
        self.ui.img_area.mouse_pressed.connect(self.mouse_pressed)
        self.ui.img_area.mouse_move.connect(self.mouse_move)
        self.ui.img_area.mouse_release.connect(self.mouse_release)
        self.ui.actionfill_color.triggered.connect(self.set_fill_color)
        self.ui.actionSet_Pixel_Range.triggered.connect(self.set_pixel_range)
        self.ui.actionCreate_Polygon.triggered.connect(self.create_polygon)
        self.ui.actionUndo.triggered.connect(self.undo)
        self.ui.actionSave.triggered.connect(self.save)

    def save(self):
        name = str(self.selected_filename.absolute())
        items = name.split('.')
        output_filename = '.'.join(items[:-1]) + '.npy'
        np.save(output_filename, self.labelimg)
        self.saved = True
        self.modified = False

    def undo(self, checked):
        if len(self.histroty) == 0:
            return
        x, y = self.histroty.pop(-1)
        self.labelimg[x, y] = 0
        pic = self.draw_points()
        self.show_pic(file_name=None, content=pic)
        self.modified = True

    def set_fill_color(self, checked):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color

    def set_pixel_range(self, checked):
        dialog = PixelRangeDialog()
        if dialog.exec_():
            v1, v2 = dialog.get_result()
            self.pixel_range = [v1, v2]
            self.logger.debug(self.pixel_range)

    def create_polygon(self, checked):
        self.state = STATE.DRAW_POLYGON

    def pos_in_img_area(self, pos: PyQt5.QtCore.QPoint):
        if self.cur_img is None:
            return False, None
        width = self.ui.img_area.width()
        height = self.ui.img_area.height()
        img_height, img_width, _ = self.cur_img.shape
        w = (width - img_width) // 2
        h = (height - img_height) // 2
        x_valid = w <= pos.x() <= w + img_width
        y_valid = h <= pos.y() <= h + img_height
        valid = x_valid and y_valid
        if valid:
            return True, (pos.x() - w, pos.y() - h)
        else:
            return False, None

    def mouse_pressed(self, ev: QMouseEvent):
        if self.state == STATE.NORMAL:
            return
        if ev.button() == Qt.LeftButton:
            pos = ev.pos()
            valid, relative_pos = self.pos_in_img_area(pos)
            self.logger.debug(valid)
            if valid:
                self.logger.debug(relative_pos)
                self.start_point = (
                    int(relative_pos[0] / self.scale), int(relative_pos[1] / self.scale))
                self.end_point = None
                self.logger.debug(self.start_point)
        elif ev.button() == Qt.RightButton:
            pass

    def mouse_move(self, ev: QMouseEvent):
        if self.state == STATE.NORMAL:
            return
        pos = ev.pos()
        valid, relative_pos = self.pos_in_img_area(pos)
        if valid:
            relative_pos = (
                int(relative_pos[0] / self.scale), int(relative_pos[1] / self.scale))
            self.draw_rect(self.start_point, relative_pos)
            if self.labelimg is not None:
                pic = self.draw_points()
                self.show_pic(file_name=None, content=pic)
            else:
                self.show_pic(file_name=None, content=self.panel_pic)

    def draw_rect(self, start_point, end_point):
        b, g, r = self.fill_color.blue(), self.fill_color.green(), self.fill_color.red()
        self.fill_color.rgb()
        start_point = (int(start_point[0] * self.scale),
                       int(start_point[1] * self.scale))
        end_point = (int(end_point[0] * self.scale),
                     int(end_point[1] * self.scale))
        self.panel_pic = cv.rectangle(
            self.cur_img.copy(), start_point, end_point, (r, g, b), 1)

    def draw_points(self):
        if self.labelimg is None:
            return
        b, g, r = self.fill_color.blue(), self.fill_color.green(), self.fill_color.red()
        x, y = np.where(self.labelimg == 1)
        temp = self.panel_pic.copy()
        for i in range(x.shape[0]):
            cv.circle(temp, (int(y[i] * self.scale),
                             int(x[i] * self.scale)), 1, (r, g, b), 1)
        return temp

    def mouse_release(self, ev: QMouseEvent):
        if self.state == STATE.NORMAL:
            return
        if ev.button() == Qt.LeftButton:
            pos = ev.pos()
            valid, relative_pos = self.pos_in_img_area(pos)
            self.logger.debug(valid)
            if valid:
                self.logger.debug(relative_pos)
                self.end_point = (
                    int(relative_pos[0] / self.scale), int(relative_pos[1] / self.scale))
        elif ev.button() == Qt.RightButton:
            if self.start_point is None or self.end_point is None:
                return
            pos = ev.pos()
            valid, relative_pos = self.pos_in_img_area(pos)
            if valid:
                click_pos = (
                    int(relative_pos[0] / self.scale), int(relative_pos[1] / self.scale))
                self.logger.debug(click_pos)
                if self.start_point[0] <= click_pos[0] <= self.end_point[
                        0] and self.start_point[1] <= click_pos[1] <= self.end_point[1]:
                    pixel_value = self.origin_img[click_pos[1],
                                                  click_pos[0], 0]
                    low, high = pixel_value + \
                        self.pixel_range[0], pixel_value + self.pixel_range[1]
                    selected_area = self.origin_img[self.start_point[1]
                        : self.end_point[1], self.start_point[0]: self.end_point[0], 0]
                    x, y = np.where((selected_area >= low) *
                                    (selected_area <= high))
                    x = x + self.start_point[1]
                    y = y + self.start_point[0]
                    self.labelimg[x, y] = 1
                    pic = self.draw_points()
                    self.show_pic(file_name=None, content=pic)
                    self.histroty.append((x, y))
                    self.modified = True

    def zoom_in_pic(self, checked):
        self.zoom_pic(True)

    def zoom_out_pic(self, checked):
        self.zoom_pic(False)

    def zoom_pic(self, zoom_in):
        if self.cur_img is None:
            return
        if zoom_in:
            if self.scale >= 5:
                pass
            elif self.scale < 1:
                self.scale += 0.1
            else:
                self.scale += 1
        else:
            if self.scale == 0:
                pass
            elif self.scale <= 1:
                self.scale -= 0.1
            else:
                self.scale -= 1
        self.logger.debug(self.scale)
        height, width, _ = self.origin_img.shape
        self.cur_img = cv.resize(self.origin_img, (int(
            height * self.scale), int(width * self.scale)), cv.INTER_LINEAR)
        if self.start_point is not None and self.end_point is not None:
            self.draw_rect(self.start_point, self.end_point)
            if self.labelimg is not None:
                pic = self.draw_points()
                self.show_pic(content=pic)
            else:
                self.show_pic(file_name=None, content=self.panel_pic)
        elif self.labelimg is not None:
            self.panel_pic = self.cur_img.copy()
            pic = self.draw_points()
            self.show_pic(file_name=None, content=pic)
        else:
            self.show_pic(file_name=None)

    def file_list_item_changed(self, item):
        if self.modified and not self.saved:
            res = QMessageBox.warning(
                self,
                'warning',
                'Changes not saved, do you want to save?',
                QMessageBox.Ok | QMessageBox.No,
                QMessageBox.Ok)
            if res == QMessageBox.Ok:
                self.save()
        base_pic_name = item.text()
        for index, filename in enumerate(self.opened_files):
            if filename.name == base_pic_name:
                selected_filename = filename
                break
        self.selected_filename = selected_filename
        self.refresh_vars()
        self.open(self.selected_filename)

    def add_tool_bar(self):
        self.toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.addAction(self.ui.actionOpen_File)
        self.toolbar.addAction(self.ui.actionOpen_Dir)
        self.toolbar.addAction(self.ui.actionSave)
        self.toolbar.addAction(self.ui.actionZoom_In)
        self.toolbar.addAction(self.ui.actionZoom_Out)
        self.toolbar.addAction(self.ui.actionfill_color)
        self.toolbar.addAction(self.ui.actionSet_Pixel_Range)
        self.toolbar.addAction(self.ui.actionCreate_Polygon)
        self.toolbar.addAction(self.ui.actionUndo)

    def show_pic(self, file_name=None, content=None):
        if file_name is not None:
            file_name = str(file_name.absolute())
            img = cv.imread(file_name)
            height, width, channel = img.shape
            self.cur_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            self.origin_img = self.cur_img
            self.labelimg = np.zeros(self.origin_img.shape[:2], dtype=np.int)
            qimg = QImage(
                self.cur_img.data,
                width,
                height,
                width * channel,
                QImage.Format_RGB888)
            self.ui.img_area.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
            self.ui.img_area.setPixmap(QPixmap.fromImage(qimg))
            self.ui.img_area.adjustSize()
        elif content is not None:
            height, width, channel = content.shape
            qimg = QImage(
                content.data,
                width,
                height,
                width * channel,
                QImage.Format_RGB888)
            self.ui.img_area.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
            self.ui.img_area.setPixmap(QPixmap.fromImage(qimg))
            self.ui.img_area.adjustSize()
        else:
            height, width, channel = self.cur_img.shape
            qimg = QImage(
                self.cur_img.data,
                width,
                height,
                width * channel,
                QImage.Format_RGB888)
            self.ui.img_area.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
            self.ui.img_area.setPixmap(QPixmap.fromImage(qimg))
            self.ui.img_area.adjustSize()

    def open_file(self, checked):
        filename, filetype = QFileDialog.getOpenFileName(
            self, '选取文件', '.', 'PNG Files(*.png);;JPG Files(*.jpg)')
        if filename == '':
            return
        filename = Path(filename)
        self.open_mode = OPEN_MODE.OPEN_FILE
        self.opened_files = [filename]
        self.selected_filename = filename
        self.open(self.selected_filename)
        self.refresh_list()

    def open_dir(self, checked):
        opened_dir = QFileDialog.getExistingDirectory(self, '打开文件夹', '.')
        if opened_dir == '':
            return
        opened_dir = Path(opened_dir)
        self.open_mode = OPEN_MODE.OPEN_DIR
        self.opened_files = list(opened_dir.iterdir())
        self.opened_files = [
            item for item in self.opened_files if util.is_pic(
                item)]
        if len(self.opened_files) == 0:
            QMessageBox.warning(self, 'warning', 'No image found')
        else:
            self.selected_filename = self.opened_files[0]
            self.open(self.selected_filename)
            self.refresh_list()

    def refresh_list(self):
        self.ui.file_list.clear()
        for file_name in self.opened_files:
            base_name = file_name.name
            self.ui.file_list.addItem(base_name)

    def open(self, filename:Path):
        self.setWindowTitle(filename.name)
        self.show_pic(file_name=filename)
        temp = str(filename).split('.')
        npy_filename = '.'.join(temp[:-1]) + '.npy'
        if os.path.exists(npy_filename):
            self.labelimg = np.load(npy_filename)
            self.panel_pic = self.cur_img.copy()
            pic = self.draw_points()
            self.show_pic(file_name=None, content=pic)


def main():
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
