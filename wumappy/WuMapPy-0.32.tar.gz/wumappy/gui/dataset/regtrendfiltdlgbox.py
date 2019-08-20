# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.regtrendfiltdlgbox
    --------------------------------------

    Regional Trend Filtering dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *  # Only used for cursor, really necessary ?
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox

from geophpy.dataset import regtrendmethod_getlist, regtrendcomp_getlist

#---------------------------------------------------------------------------#
# Regional Trend Filtering Dialog Box Object                                #
#---------------------------------------------------------------------------#
class RegTrendFiltDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent, nxsize=3, nysize=3, method='rel', component='loc'):
        '''
        '''
        
        window = cls()
        window.parent = parent
        window.dataset = parent.dataset
        window.originaldataset = parent.dataset
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.zmin = window.parent.zmin
        window.zmax = window.parent.zmax
        zmin, zmax = window.dataset.histo_getlimits()
        if window.zmin is None:
            window.zmin = zmin
        if window.zmax is None:
            window.zmax = zmax            

        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.nxsize = nxsize
        window.nysize = nysize
        window.method = method
        window.component = component
        window.items_list = [#
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # ELEMENT_NAME - ELEMENT_ID - COLUMN - ROW - FUNCTION_INIT - FUNCTION_UPDATE - NUM_GROUPBOX - (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN
                           #------------------------------------------------------------------------
                           ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 1, 1, 3, 2],
                           ['GroupBox', 'LOCTREND_ID', 0, 1, False, None, None, 2, 0, 1, 1, 1],
                           ['GroupBox', 'REGTREND_ID', 0, 1, False, None, None, 2, 0, 1, 1, 1],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Filter options #######################################################
                           ['Label', 'FILTERNXSIZE_ID', 0, 0, False, None, None, 0],  
                           ['SpinBox', '', 1, 0, True, window.NxSizeInit, window.NxSizeUpdate, 0],    
                           #['Label', '', 2, 0, False, None, None, 0],
                           ['CheckBox', 'SQUARE_PIXEL', 2, 0, True, window.SquareInit, window.SquareUpdate, 0],  
                           ['Label', 'FILTERNYSIZE_ID', 3, 0, False, window.NySizeLabelInit, None, 0],  
                           ['SpinBox', '', 4, 0, True, window.NySizeInit, window.NySizeUpdate, 0],    
                           ['Label', '', 5, 0, False, None, None, 0],  
                           ['Label', 'REGTRENDMETHOD_ID', 6, 0, False, None, None, 0],  
                           ['ComboBox', '', 7, 0, True, window.MethodInit, window.MethodUpdate, 0],   
                           ['Label', '', 8, 0, False, None, None, 0],  
                           ['Label', 'REGTRENDCOMPONENT_ID', 9, 0, False, None, None, 0],  
                           ['ComboBox', '', 10, 0, True, window.ComponentInit, window.ComponentUpdate, 0],   
                           ['Label', '', 11, 0, False, None, None, 0],  
                           ## Cancel, Update, Valid ################################################
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],   
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],   
                           ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],
                           ## Local trend ##########################################################
                           ['Graphic', '', 0, 1, False, window.LocTrendImageInit, None, 2],
                           ## Regional trend #######################################################
                           ['Graphic', '', 0, 1, False, window.RegTrendImageInit, None, 3]]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window

    #--------------------------------------------------------------------------#
    # Filter options TAB                                                       #
    #--------------------------------------------------------------------------#
    def DisplayUpdate(self):
        '''Updates the GUI at the change of a filter's parameter.'''

        # Auto updating GUI
        if self.realtimeupdateflag:
            self.CartoImageUpdate()

        # Manually updating GUI
        else:
            # Disabling Rendering and Valid to indicate
            # display not yet uptaded.
            # Enabling Update display button.
            self.LocTrendImageId.setEnabled(False)
            self.RegTrendImageId.setEnabled(False)
            self.ValidButtonId.setEnabled(False)
            self.DispUpdateButtonId.setEnabled(True)

    def NxSizeInit(self, Id=None):
        if Id is not None:
            Id.setRange(3, 101)
            Id.setSingleStep(2)
            Id.setValue(self.nxsize)
        self.NxSizeId = Id
        return Id

    def NxSizeUpdate(self):
        self.nxsize = self.NxSizeId.value()
        if self.square_pixel.isChecked():
            self.NySizeId.setValue(self.nxsize)
            self.NySizeUpdate()

        self.DisplayUpdate()

    def NySizeInit(self, Id=None):
        if Id is not None:
            Id.setRange(3, 101)
            Id.setSingleStep(2)
            Id.setValue(self.nysize)
            Id.setEnabled(False)

        self.NySizeId = Id

        return Id

    def NySizeUpdate(self):
        self.nysize = self.NySizeId.value()
        self.DisplayUpdate()

    def NySizeLabelInit(self, Id=None):
        if Id is not None:
            square_pixel_flag = self.square_pixel.isChecked()
            Id.setEnabled(not square_pixel_flag)

        self.NySizeLabelId = Id
        return Id  

    def SquareInit(self, Id=None):
        if Id is not None:
            Id.setChecked(True)
            self.square_pixel = Id

        return Id

    def SquareUpdate(self):
        square_pixel_flag = self.square_pixel.isChecked()
        self.NySizeId.setEnabled(not square_pixel_flag)
        self.NySizeLabelId.setEnabled(not square_pixel_flag)
        self.NxSizeUpdate()

    def MethodInit(self, Id=None):
        lst = regtrendmethod_getlist()
        Id.addItems(lst)
        try:
            index = Id.findText(self.method)
        except:
            index = 0
        Id.setCurrentIndex(index)
        self.MethodId = Id
        return Id

    def MethodUpdate(self):
        self.method = self.MethodId.currentText()
        self.DisplayUpdate()

    def ComponentInit(self, Id=None):
        lst = regtrendcomp_getlist()
        Id.addItems(lst)
        try:
            index = Id.findText(self.component)
        except:
            index = 0
        Id.setCurrentIndex(index)
        self.ComponentId = Id
        return Id

    def ComponentUpdate(self):
        self.component = self.ComponentId.currentText()
        self.DisplayUpdate()

    #--------------------------------------------------------------------------#
    # Cancel, Update, Valid button TAB                                         #
    #--------------------------------------------------------------------------#
    def DispUpdateButtonInit(self, Id=None):
        self.DispUpdateButtonId = Id
        Id.setHidden(self.realtimeupdateflag)       # Hides button if real time updating activated
        Id.setEnabled(False)                        # disables the button , by default
        return Id

    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                     # updates carto image
        
    def ValidButtonInit(self, Id=None):
        self.ValidButtonId = Id
        return Id

    def CancelButtonInit(self, Id=None):
        self.CancelButtonId = Id
        return Id

    #--------------------------------------------------------------------------#
    # Local trend TAB                                                          #
    #--------------------------------------------------------------------------#
    def LocTrendImageInit(self, Id=None):
        self.loctrendfig = None
        self.LocTrendImageId = Id
        return Id

    #--------------------------------------------------------------------------#
    # Regional trend TAB                                                       #
    #--------------------------------------------------------------------------#
    def RegTrendImageInit(self, Id=None):
        self.regtrendfig = None
        self.RegTrendImageId = Id
        self.CartoImageUpdate()
        return Id

    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        # processes data set
        self.dataset_local = self.originaldataset.copy()
        self.dataset_local.regtrend(nx=self.nxsize, ny=self.nysize, method=self.method, component="local")

        self.dataset_regional = self.originaldataset.copy()
        self.dataset_regional.regtrend(nx=self.nxsize, ny=self.nysize, method=self.method, component="regional")

        if self.component=="local":
            self.dataset = self.dataset_local.copy()
            
        elif self.component=="regional":
            self.dataset = self.dataset_regional.copy()

        # plots geophysical image
        self.loctrendfig, _ = self.dataset_local.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.loctrendfig, interpolation=self.parent.interpolation, cmmin=self.zmin, cmmax=self.zmax, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)
        self.LocTrendImageId.update(self.loctrendfig)

        #loctrendpixmap = QPixmap.grabWidget(FigureCanvas(self.loctrendfig))
        #loctrendpixmap = loctrendpixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.LocTrendImageId.setPixmap(loctrendpixmap)

        self.regtrendfig, _ = self.dataset_regional.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.regtrendfig, interpolation=self.parent.interpolation, cmmin=self.zmin, cmmax=self.zmax, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)
        self.RegTrendImageId.update(self.regtrendfig)

        #regtrendpixmap = QPixmap.grabWidget(FigureCanvas(self.regtrendfig))
        #regtrendpixmap = regtrendpixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.RegTrendImageId.setPixmap(regtrendpixmap)

        self.LocTrendImageId.setEnabled(True)                              # enables the local trend image
        self.RegTrendImageId.setEnabled(True)                              # enables the regional trend image

        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button

        self.wid.setCursor(initcursor)                                  # resets the init cursor
        
