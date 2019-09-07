#-------------------------------------------------------------------------------
# Name:        Utils
# Purpose:
#
# Author:      Elbar
#
# Created:     01/03/2012
# Copyright:   (c) USER 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from PyQt5 import QtWidgets
import logging

#-------------------------------------------------------------------------------
def errorMessageBox(msg):
    ''' Mesaage Box '''
    QtWidgets.QMessageBox.critical(None,"Error",msg,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.NoButton)

#-------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
def check_input(val, msg, non_zero = True):
    ''' check input value'''
    try:
        _val = float(val)
    except:
        _val = 0.0
    if ((_val > 0.0 and non_zero) or
        (_val >= 0.0 and not non_zero)):
        return _val, True
    else:
        errorMessageBox(msg)
        return None, False
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class ConsoleHandler(logging.Handler):
    """This class is a logger handler. It prints on the console"""

    def __init__(self):
        """Constructor"""
        logging.Handler.__init__(self)

    def emit(self, record):
        """format and print the record on the console"""
        print(self.format(record))
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class DummyHandler(logging.Handler):
    """This class is a logger handler. It doesn't do anything"""

    def __init__(self):
        """Constructor"""
        logging.Handler.__init__(self)

    def emit(self, record):
        """do nothinbg with the given record"""
        pass
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def create_logger(logger_name=None, level=logging.DEBUG):
    ''' Create a logger '''
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s")
    stream_handler = ConsoleHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
def set_up_logger_file(logger,file_name):
    ''' Set up a file for logger '''
    fh = logging.FileHandler(file_name, 'w')
    frm = logging.Formatter("%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s")
    fh.setFormatter(frm)
    logger.addHandler(fh)

#-------------------------------------------------------------------------------