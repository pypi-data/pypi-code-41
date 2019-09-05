# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modul is used for GUI of Lisa
"""

from loguru import logger

# from scaffan import image
from pathlib import Path
import sys
import os.path as op
import datetime
# import io3d.misc
from io3d import cachefile
import json
import time
import platform

# import PyQt5.QtWidgets
# print("start 3")
# from PyQt5.QtWidgets import QApplication, QFileDialog
# print("start 4")
from PyQt5 import QtGui

# print("start 5")
from pyqtgraph.parametertree import Parameter, ParameterTree
import pyqtgraph.widgets
import pyqtgraph.widgets

# print("start 6")

import io3d
import io3d.datasets
pth = str(Path(__file__).parent / "../../exsu/")
logger.debug(f"exsu path: {pth}")
sys.path.insert(0, pth)
import exsu
logger.debug(f"exsu path 2: {exsu.__file__}")
from exsu.report import Report

# import scaffan.lobulus
# import scaffan.report
# import scaffan.skeleton_analysis
# from .report import Report
# import scaffan.evaluation
# from scaffan.pyqt_widgets import BatchFileProcessingParameter
from . import activity_detector


class AnimalWatch:
    def __init__(self):

        self.report: exsu.report.Report = exsu.report.Report()
        self.report.set_save(True)
        # self.report.level = 50

        self.raise_exception_if_color_not_found = True

        # import scaffan.texture as satex
        # self.glcm_textures = satex.GLCMTextureMeasurement()
        # self.lobulus_processing = scaffan.lobulus.Lobulus()
        # self.skeleton_analysis = scaffan.skeleton_analysis.SkeletonAnalysis()
        # self.evaluation = scaffan.evaluation.Evaluation()

        # self.lobulus_processing.set_report(self.report)
        # self.glcm_textures.set_report(self.report)
        # self.skeleton_analysis.set_report(self.report)
        # self.evaluation.report = self.report
        self.activity_detector:activity_detector.ActivityDetector = activity_detector.ActivityDetector(
            report=self.report)
        self.win:QtGui.QWidget = None
        self.cache = cachefile.CacheFile("~/.exsu_cache.yaml")
        # self.cache.update('', path)
        common_spreadsheet_file = self.cache.get_or_save_default(
            "common_spreadsheet_file", self._prepare_default_output_common_spreadsheet_file())
        logger.debug("common_spreadsheet_file loaded as: {}".format(common_spreadsheet_file))
        params = [
            {
                "name": "Input",
                "type": "group",
                "children": [
                    {"name": "Directory Path", "type": "str"},
                    {"name": "Select", "type": "action"},
                    {"name": "Data Info", "type": "str", "readonly": True},
                    {"name": "Camera ID", "type": "str"}
                ],
            },
            {
                "name": "Output",
                "type": "group",
                "children": [
                    {
                        "name": "Directory Path",
                        "type": "str",
                        "value": self._prepare_default_output_dir(),
                    },
                    {"name": "Select", "type": "action"},
                    # {
                    #     "name": "Common Spreadsheet File",
                    #     "type": "str",
                    #     "value": common_spreadsheet_file,
                    # },
                    # {"name": "Select Common Spreadsheet File", "type": "action",
                    #  "tip": "All measurements are appended to this file in addition to data stored in Output Directory Path."
                    #  },
                ],
            },
            {
                "name": "Processing",
                "type": "group",
                "children": [
                    # {'name': 'Directory Path', 'type': 'str', 'value': prepare_default_output_dir()},
                    {
                        'name': "Anwa dir",
                        "type": 'str',
                        'value': self._prepare_anwa_dir()
                    },
                    self.activity_detector.parameters,
                    # {
                    #     "name": "Show",
                    #     "type": "bool",
                    #     "value": False,
                    #     "tip": "Show images",
                    # },
                    # {
                    #     "name": "Open output dir",
                    #     "type": "bool",
                    #     "value": False,
                    #     "tip": "Open system window with output dir when processing is finished",
                    # },
                    # {
                    #     "name": "Run Skeleton Analysis",
                    #     "type": "bool",
                    #     "value": True,
                    #     # "tip": "Show images",
                    # },
                    # {
                    #     "name": "Run Texture Analysis",
                    #     "type": "bool",
                    #     "value": True,
                    #     # "tip": "Show images",
                    # },
                    # {
                    #     "name": "Report Level",
                    #     "type": "int",
                    #     "value": 50,
                    #     "tip": "Control ammount of stored images. 0 - all debug imagess will be stored. "
                    #            "100 - just important images will be saved.",
                    # },
                ],
            },
            {"name": "Run", "type": "action"},
        ]
        self.parameters = Parameter.create(name="params", type="group", children=params)
        # here is everything what should work with or without GUI
        # self.parameters.param("Input", "File Path").sigValueChanged.connect(
        #     self._get_file_info
        # )
        # self.anim: image.AnnotatedImage = None
        pass

    def _prepare_default_output_common_spreadsheet_file(self):
        pass

    def _prepare_default_output_dir(self):
        default_dir = io3d.datasets.join_path("lynx_lynx", "processed", "anwa", get_root=True)
        return default_dir

    def _prepare_anwa_dir(self):
        anwa_dir = Path("~/.anwa")
        return anwa_dir

    def select_input_dir_gui(self):
        from PyQt5 import QtWidgets

        default_dir = io3d.datasets.join_path(get_root=True)
        # default_dir = op.expanduser("~/data")
        if not op.exists(default_dir):
            default_dir = op.expanduser("~")

        # dialog = QtWidgets.QFileDialog()
        # dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        # dialog.exec();
        fn = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select Input Directory",
            directory=default_dir,
            # filter="NanoZoomer Digital Pathology Image(*.ndpi)",
        )
        self.set_input_dir(fn)

    def set_input_dir(self, fn):
        fn = str(fn)
        fnparam = self.parameters.param("Input", "Directory Path")
        fnparam.setValue(fn)
        logger.debug("Set Input File Path to : {}".format(fn))
        # import pdb; pdb.set_trace()
        # print("ahoj")

    def set_output_dir(self, path):
        fnparam = self.parameters.param("Output", "Directory Path")
        fnparam.setValue(str(path))

    def set_report_level(self, level:int):
        fnparam = self.parameters.param("Processing", "Report Level")
        fnparam.setValue(level)

    def set_common_spreadsheet_file(self, path):
        fnparam = self.parameters.param("Output", "Common Spreadsheet File")
        fnparam.setValue(path)
        self.cache.update('common_spreadsheet_file', path)
        logger.debug("common_spreadsheet_file set to {}".format(path))
        print("common_spreadsheet_file set to {}".format(path))

    def select_output_dir_gui(self):
        from PyQt5 import QtWidgets

        default_dir = self._prepare_default_output_dir()
        if op.exists(default_dir):
            start_dir = default_dir
        else:
            start_dir = op.dirname(default_dir)

        fn = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select Output Directory",
            directory=start_dir,
            # filter='All Files(*.*)',
            # filter="NanoZoomer Digital Pathology Image(*.ndpi)"
        )
        # print (fn)
        self.set_output_dir(fn)

    def run(self):

        odir = str(self.parameters.param("Output", "Directory Path").value())
        idir = str(self.parameters.param("Input", "Directory Path").value())
        # = str(self.parameters.param("Output", "Directory Path").value())
        # odir = float(self.parameters.param("Output", "Directory Path").value())
        self.report.level = 30

        logger.debug(f"output dir {odir}")
        self.report.init_with_output_dir(odir)
        # self.report.outputdir = odir
        Path(odir).mkdir(parents=True, exist_ok=True)
        self.activity_detector.set_input_path(idir)
        self.activity_detector.set_output_path(odir)
        self.activity_detector.run()

    def start_gui(self, skip_exec=False, qapp=None):

        from PyQt5 import QtWidgets
        import anwa.qtexceptionhook

        # import QApplication, QFileDialog
        if not skip_exec and qapp == None:
            qapp = QtWidgets.QApplication(sys.argv)

        self.parameters.param("Input", "Select").sigActivated.connect(
            self.select_input_dir_gui
        )
        self.parameters.param("Output", "Select").sigActivated.connect(
            self.select_output_dir_gui
        )
        # self.parameters.param("Output", "Select Common Spreadsheet File").sigActivated.connect(
        #     self.select_output_spreadsheet_gui
        # )
        self.parameters.param("Run").sigActivated.connect(
            self.run
        )

        # self.parameters.param("Processing", "Open output dir").setValue(True)
        t = ParameterTree()
        t.setParameters(self.parameters, showTop=False)
        # t.setWindowTitle("pyqtgraph example: Parameter Tree")
        # t.show()

        # print("run scaffan")
        win = QtGui.QWidget()
        win.setWindowTitle("AnWa {}".format(anwa.__version__))
        logo_fn = op.join(op.dirname(__file__), "anwa.png")
        app_icon = QtGui.QIcon()
        # app_icon.addFile(logo_fn, QtCore.QSize(16, 16))
        app_icon.addFile(logo_fn)
        win.setWindowIcon(app_icon)
        # qapp.setWindowIcon(app_icon)
        layout = QtGui.QGridLayout()
        win.setLayout(layout)
        pic = QtGui.QLabel()
        pic.setPixmap(QtGui.QPixmap(logo_fn).scaled(100, 100))
        pic.show()
        # layout.addWidget(QtGui.QLabel("These are two views of the same data. They should always display the same values."), 0,  0, 1, 2)
        layout.addWidget(pic, 1, 0, 1, 1)
        layout.addWidget(t, 2, 0, 1, 1)
        # layout.addWidget(t2, 1, 1, 1, 1)

        win.show()
        win.resize(800, 800)
        self.win = win
        # win.
        if not skip_exec:

            qapp.exec_()

