#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import os
import sys
from datetime import datetime
import argparse
import logging
import getpass

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings

from src.libs.lib import newIcon
from src.libs.crashreporter import excepthook
from src.gui.LabelerWindow import LabelerWindow
from src.api.inference_api import InferenceApi


class ActiveImageLabelerWindow(LabelerWindow):

    def __init__(self):
        super(ActiveImageLabelerWindow, self).__init__()
        
        # read server parameters
        print('Reading Settings')
        settings = QSettings('KAUST_IVUL', 'ActiveImageLabeler')
        # set server parameters
        self.serverHost.setText(settings.value('serverHost', "localhost", str))
        self.serverPort.setValue(settings.value('serverPort', 8000, int))
        

    def closeEvent(self, event):
        
        # save server parameters
        print('Saving Settings')
        settings = QSettings('KAUST_IVUL', 'ActiveImageLabeler')
        # read server parameters
        settings.setValue('serverHost', self.serverHost.text())
        settings.setValue('serverPort', self.serverPort.value())



def main():
    '''construct main app and run it'''

    # Argument Parser
    parser = argparse.ArgumentParser(
        description="Image Labeler based on Active Learning")
    parser.add_argument("--host",
                default="127.0.0.1",
                type=str,
                help="host to connect to API")

    parser.add_argument("--port",
                        default=8000,
                        type=int,
                        help="port to connect to API")

    parser.add_argument("--project",
                        default=None,
                        type=str,
                        help="open a project")

    parser.add_argument("--logdir",
                        default="log",
                        type=str,
                        help="diretory for logging")

    parser.add_argument("--loglevel",
                        default="INFO",
                        type=str,
                        help="diretory for logging")

    args = parser.parse_args()
        
    # define logging level (DEBUG/INFO/WARNING/ERROR)
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)

    # set up logging configuration
    log_file = os.path.join(args.logdir, datetime.now().strftime('%Y-%m-%d %H-%M-%S.log'))
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=20, # INFO
        format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
        handlers=[
            # file handler
            logging.FileHandler(log_file),
            # stream handler
            logging.StreamHandler()
        ])
    logging.info(f"Start logging on {log_file}")



    if getpass.getuser() not in "ramazam, giancos":
        # send report on SLACK for users different from the authors
        sys.excepthook = excepthook

    # create QtApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Seeds Labeler")
    app.setWindowIcon(newIcon("shape_t"))

    # Create GUI
    win = ActiveImageLabelerWindow()
    # Create API    
    api = InferenceApi(win.serverHost.text(), win.serverPort.value())

    
    # Connect API to GUI
    win.serverHost.textChanged.connect(api.setHost)
    win.serverPort.valueChanged.connect(api.setPort)
    # GUI detection button connected to API Object Detection
    # (parameter is OpenCV Image)
    win.detect.triggered.connect(lambda: api.detectObjects(win.currentImage.path))

    # API Object Found connected to Window add Shape to current Image
    api.objectFound.connect(win.addShape)
    api.objectsFound.connect(win.addShapes)
    api.errorWithInference.connect(win.errorMessage)

    # Show window and run QtApplication
    win.showMaximized()

    # open project if asked to with arguments
    if args.project is not None:
        win.openProject(args.project)

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())