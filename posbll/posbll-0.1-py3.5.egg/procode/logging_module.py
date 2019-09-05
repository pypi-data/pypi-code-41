# coding=utf-8

from blltoapp_interface import BllToAppInterface

class Loggingm(object):
    def __init__(self):
        pass
    @classmethod
    def write_error(self,jsonparam):
        bll=BllToAppInterface("loggerm","write_error")
        bll.executefun(jsonparam)