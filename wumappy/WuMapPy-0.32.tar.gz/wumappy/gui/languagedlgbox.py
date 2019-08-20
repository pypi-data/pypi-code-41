# -*- coding: utf-8 -*-
'''
    wumappy.gui.languagedlgbox
    --------------------------

    Language dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import absolute_import

from wumappy.gui.common.griddlgbox import GridDlgBox
#from geophpy.dataset import *

#---------------------------------------------------------------------------#
# Language Dialog Box Object                                                #
#---------------------------------------------------------------------------#
class LanguageDlgBox:
    
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
        window.items_list = [
            ['Label', 'LANGUAGE_ID', 0, 0, False, None, None], 
            ['ComboBox', '', 0, 1, True, window.LanguageInit, window.LanguageUpdate],   
            ['ValidButton', 'VALID_ID', 1, 1, True, window.ValidButtonInit, None],   
            ['CancelButton', 'CANCEL_ID', 1, 0, True, window.CancelButtonInit, None]
            ]

        dlgbox = GridDlgBox(title, parent, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window


    def LanguageInit(self, Id=None):
                                                    # building of the "language" field to select in a list
        lnglist = self.asciiset.getLanguageList()
        try:
            lngindex = lnglist.index(self.asciiset.lnglist[self.asciiset.lngindex].name)
        except:
            lngindex = 0
            
        if (Id is not None):
            Id.addItems(lnglist)
            Id.setCurrentIndex(lngindex)
        self.LanguageId = Id
        return Id


    def LanguageUpdate(self):
        self.asciiset.lngname = self.LanguageId.currentText()
        self.asciiset.lngindex = self.LanguageId.currentIndex()


    def ValidButtonInit(self, Id=None):
        self.ValidButtonId = Id
        return Id


    def CancelButtonInit(self, Id=None):
        self.CancelButtonId = Id
        return Id


