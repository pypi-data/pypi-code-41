# -*- coding: utf-8 -*-
'''
    wumappy.gui.guisettingsdlgbox
    -----------------------------

    Graphical User Interface settings dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import absolute_import

from wumappy.gui.common.griddlgbox import GridDlgBox
#from geophpy.dataset import *

#---------------------------------------------------------------------------#
# GUI Settings Dialog Box Object                                            #
#---------------------------------------------------------------------------#
class GuiSettingsDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent):
        '''
        '''

        window = cls()
        window.title = title
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.changeresolutionflag = window.configset.getboolean('MISC', 'changeresolutionflag')
        window.items_list = [
            ['CheckBox', 'RTUPDATE_ID', 0, 0, True, window.RealTimeUpdateInit, window.RealTimeUpdateUpdate],
            ['CheckBox', 'CHANGE_RESOLUTION_ID', 1, 0, True, window.ChangeResolutionInit, window.ChangeResolutionUpdate],
            ['ValidButton', 'VALID_ID', 2, 1, True, window.ValidButtonInit, None],   
            ['CancelButton', 'CANCEL_ID', 2, 0, True, window.CancelButtonInit, None]
            ]

        dlgbox = GridDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window


    def RealTimeUpdateInit(self, Id=None):
        if (Id is not None):
            Id.setChecked(self.realtimeupdateflag)
        self.RealTimeUpdateId = Id
        return Id


    def RealTimeUpdateUpdate(self):
        self.realtimeupdateflag = self.RealTimeUpdateId.isChecked()


    def ChangeResolutionInit(self, Id=None):
        if (Id is not None):
            Id.setChecked(self.changeresolutionflag)
        self.ChangeResolutionId = Id
        return Id


    def ChangeResolutionUpdate(self):
        self.changeresolutionflag = self.ChangeResolutionId.isChecked()



    def ValidButtonInit(self, Id=None):
        self.ValidButtonId = Id
        return Id


    def CancelButtonInit(self, Id=None):
        self.CancelButtonId = Id
        return Id


