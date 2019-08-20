# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.polereductiondlgbox
    ---------------------------------------

    Pôle reduction dialog box management.

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

#---------------------------------------------------------------------------#
# Pôle reduction Dialog Box Object                                          #
#---------------------------------------------------------------------------#
class PoleReductionDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent, apod=0, inclineangle=65, alphaangle=0):
        '''
        '''
        
        window = cls()
        window.parent = parent
        window.dataset = parent.dataset
        window.originaldataset = parent.dataset
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.apod = apod
        window.inclineangle = inclineangle
        window.alphaangle = alphaangle
        window.items_list = [
            # TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN,[GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
            # GroupBox ---------------------------------------------------------
            ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
            ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 1, 1, 4, 2],
            ['GroupBox', 'RENDERING_ID', 0, 2, False, None, None, 1, 0, 1, 1, 1],
            # Filter options --------------------------------------------------
            ['Label', 'APODISATIONFACTOR_ID', 0, 0, False, None, None, 0],  
            ['SpinBox', '', 1, 0, True, window.ApodisationFactorInit, window.ApodisationFactorUpdate, 0],    
            ['Label', 'APODISATIONFACTOR_MSG', 2, 0, False, None, None, 0],
            ['Label', 'INCLINEANGLE_ID', 3, 0, False, None, None, 0],  
            ['DoubleSpinBox', '', 4, 0, True, window.InclineAngleInit, window.InclineAngleUpdate, 0],    
            ['Label', 'ALPHAANGLE_ID', 5, 0, False, None, None, 0],  
            ['DoubleSpinBox', '', 6, 0, True, window.AlphaAngleInit, window.AlphaAngleUpdate, 0],  
            ['Label', '', 7, 0, False, None, None, 0], 
            ['Label', '', 8, 0, False, None, None, 0], 
            ['Label', '', 9, 0, False, None, None, 0],   
            ['Label', '', 10, 0, False, None, None, 0], 
            # Cancel, Update, Valid --------------------------------------------
            ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],   
            ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],   
            ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],   
            # Rendering --------------------------------------------------------
            ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 2]
            ]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window


    def ApodisationFactorInit(self, id=None):
        if (id != None):
            id.setRange(0, 25)
            id.setSingleStep(5)
            id.setValue(self.apod)
        self.ApodisationFactorId = id
        return id


    def ApodisationFactorUpdate(self):
        self.apod = self.ApodisationFactorId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def InclineAngleInit(self, id=None):
        if (id != None):
            id.setRange(0.1, 90)
            id.setValue(self.inclineangle)
        self.InclineAngleId = id
        return id


    def InclineAngleUpdate(self):
        self.inclineangle = self.InclineAngleId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def AlphaAngleInit(self, id=None):
        if (id != None):
            id.setRange(0, 360)
            id.setValue(self.alphaangle)
        self.AlphaAngleId = id
        return id


    def AlphaAngleUpdate(self):
        self.alphaangle = self.AlphaAngleId.value()
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)                   # Hides button if real time updating activated
        id.setEnabled(False)                                    # disables the button , by default
        return id


    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                                 # updates carto image
        

    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id


    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id


    def CartoImageInit(self, id=None):
        self.cartofig = None
        self.CartoImageId = id
        self.CartoImageUpdate()
        return id


    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        # processes data set
        self.dataset = self.originaldataset.copy()
        self.dataset.polereduction(apod=self.apod, inclination=self.inclineangle, magazimuth=self.alphaangle)

        # plots geophysical image
        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.cartofig, interpolation=self.parent.interpolation, cmmin=self.parent.zmin, cmmax=self.parent.zmax, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)
        self.CartoImageId.update(self.cartofig)

        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
        #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))    # builds the pixmap from the canvas
        #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CartoImageId.setPixmap(cartopixmap)

        self.CartoImageId.setEnabled(True)                              # enables the carto image
        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button
        
        self.wid.setCursor(initcursor)                                  # resets the init cursor
