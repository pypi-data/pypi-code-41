# -.- coding: utf-8 -.-
__author__ = 'gallochri'
__version__ = '0.0.1'
__license__ = 'GPLv3 license'

import os

from PyPDF2.pdf import PdfFileReader, PdfFileWriter, PageObject
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

from glBooklet.mainwindow_ui import Ui_MainWindow

user_home = str(os.path.expanduser('~'))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.go_button.clicked.connect(self.go_button_clicked)
        self.select_file.clicked.connect(self.select_file_clicked)
        self.select_dir.clicked.connect(self.select_dir_clicked)
        self.test_checkbox.stateChanged.connect(self.test_print)
        self.front_checkbox.stateChanged.connect(self.front_pages)
        self.back_checkbox.stateChanged.connect(self.back_pages)

        def action_about():
            QApplication.instance().aboutQt()
        self.action_about.triggered.connect(action_about)

    def select_file_clicked(self):
        pdf_file = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         str("Select a PDF file"),
                                                         user_home,
                                                         str("PDF Files (*.pdf)")
                                                         )[0]
        self.select_dir.setEnabled(True)
        self.selected_dir.setEnabled(True)
        self.go_button.setEnabled(True)
        self.scale_slider.setEnabled(True)
        self.scale_spinbox.setEnabled(True)
        self.test_checkbox.setEnabled(True)
        self.front_checkbox.setEnabled(True)
        self.back_checkbox.setEnabled(True)
        self.selected_file.setText(pdf_file)
        self.selected_dir.setText(os.path.dirname(pdf_file))

    def select_dir_clicked(self):
        self.selected_dir.setText(QtWidgets.QFileDialog.getExistingDirectory(self))

    def test_print(self):
        if self.test_checkbox.isChecked():
            self.test_spinbox.setEnabled(True)
        else:
            self.test_spinbox.setEnabled(False)

    def front_pages(self):
        if self.front_checkbox.isChecked():
            self.fs_left_tx_spinbox.setEnabled(True)
            self.fs_right_tx_spinbox.setEnabled(True)
            self.fs_ty_spinbox.setEnabled(True)
        else:
            self.fs_left_tx_spinbox.setEnabled(False)
            self.fs_right_tx_spinbox.setEnabled(False)
            self.fs_ty_spinbox.setEnabled(False)

    def back_pages(self):
        if self.back_checkbox.isChecked():
            self.bs_left_tx_spinbox.setEnabled(True)
            self.bs_right_tx_spinbox.setEnabled(True)
            self.bs_ty_spinbox.setEnabled(True)
        else:
            self.bs_left_tx_spinbox.setEnabled(False)
            self.bs_right_tx_spinbox.setEnabled(False)
            self.bs_ty_spinbox.setEnabled(False)

    def back_checked(self):
        self.fb_left_tx_spinbox.setEnabled(True)
        self.fb_right_tx_spinbox.setEnabled(True)
        self.fb_ty_spinbox.setEnabled(True)

    # TODO
    def go_button_clicked(self):
        pdf_file = self.selected_file.text()
        directory = self.selected_dir.text()
        spinbox_scale = self.scale_spinbox.value()
        test_print = self.test_checkbox.checkState()
        scale = spinbox_scale/100

        from datetime import datetime
        start_time = datetime.now()
        print("pdf ->  " + pdf_file)
        print("output_dir ->  " + directory)
        print("Scale ->", scale)

        paired_pages = PdfFileWriter()
        for page in PdfFileReader(open(pdf_file, "rb")).pages:
            paired_pages.addPage(page)

        if test_print != 0:
            pages_count = self.test_spinbox.value()
        else:
            pages_count = paired_pages.getNumPages()
        print("pages ->  ", pages_count)

        front_side_pages = zip(range(1, pages_count, 4), range(3, pages_count, 4))
        back_side_pages = zip(range(2, pages_count, 4), range(0, pages_count, 4))

        front_output = PdfFileWriter()
        back_output = PdfFileWriter()
        size = 841 / 2

        fs_left_tx = self.fs_left_tx_spinbox.value()
        fs_right_tx = self.fs_right_tx_spinbox.value()
        fs_ty = self.fs_ty_spinbox.value()

        fb_left_tx = self.bs_left_tx_spinbox.value()
        fb_right_tx = self.bs_right_tx_spinbox.value()
        fb_ty = self.bs_ty_spinbox.value()

        for index, page in enumerate(front_side_pages):
            page_model = PageObject.createBlankPage(width=841, height=595)
            page_model.mergeScaledTranslatedPage(paired_pages.getPage(page[0]), tx=fs_left_tx, ty=fs_ty, scale=scale)
            page_model.mergeScaledTranslatedPage(paired_pages.getPage(page[1]), tx=size+fs_right_tx, ty=fs_ty, scale=scale)
            front_output.addPage(page_model)

        for index, page in enumerate(back_side_pages):
            page_model = PageObject.createBlankPage(width=841, height=595)
            page_model.mergeScaledTranslatedPage(paired_pages.getPage(page[0]), tx=fb_left_tx, ty=fb_ty, scale=scale)
            page_model.mergeScaledTranslatedPage(paired_pages.getPage(page[1]), tx=size+fb_right_tx, ty=fb_ty, scale=scale)
            back_output.addPage(page_model)

        with open(os.path.join(directory, "1_front_side - " + os.path.basename(pdf_file)), "wb") as stream:
            print("Writing files...")
            front_output.write(stream)

        with open(os.path.join(directory, "2_back_side - " + os.path.basename(pdf_file)), "wb") as stream:
            print("Writing files...")
            back_output.write(stream)

        finish_time = datetime.now()
        dur = finish_time - start_time
        print("Time ->", dur)
