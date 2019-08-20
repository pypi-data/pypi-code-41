# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.analyticsignaldlgbox
    ----------------------------------------

    Analytic signal dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
#from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox

#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure

#SIZE_GRAPH_x = 440

#---------------------------------------------------------------------------#
# Analytic signal Dialog Box Object                                         #
#---------------------------------------------------------------------------#
class AnalyticSignalDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent, apod=0):
        '''
        '''
        
        window = cls()
        window.firstdisplayflag = True             # True if first display of dialog box, False in the others cases
        window.parent = parent
        window.dataset = parent.dataset
        window.originaldataset = parent.dataset
        window.colormap = parent.dataset.info.cmapname
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.automaticrangeflag = True
        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.apod = apod
        window.items_list = [#
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # ELEMENT_NAME - ELEMENT_ID - COLUMN - ROW - FUNCTION_INIT - FUNCTION_UPDATE - NUM_GROUPBOX - (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN
                           #------------------------------------------------------------------------
                           ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 1, 1, 3, 2],
                           ['GroupBox', 'RENDERING_ID', 0, 2, False, None, None, 2, 0, 1, 1, 1],
                           ['GroupBox', 'HISTOGRAM_ID', 0, 1, False, None, None, 3, 0, 1, 1, 1],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Filter options #######################################################
                           ['Label', 'APODISATIONFACTOR_ID', 0, 0, False, None, None, 0],  
                           ['SpinBox', '', 1, 0, True, window.ApodisationFactorInit, window.ApodisationFactorUpdate, 0],    
                           ['Label', 'APODISATIONFACTOR_MSG', 2, 0, False, None, None, 0],
                           ['Label', 'MINIMALVALUE_ID', 3, 0, False, None, None, 0],  
                           ['SpinBox', '', 4, 0, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 0],    
                           ['Slider', '', 5, 0, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 0],   
                           ['Label', 'MAXIMALVALUE_ID', 6, 0, False, None, None, 0],  
                           ['SpinBox', '', 7, 0, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 0],    
                           ['Slider', '', 8, 0, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 0],
                           ['Label', '', 9, 0, False, None, None, 0],  
                           ['Label', '', 10, 0, False, None, None, 0],  
                           ['Label', '', 11, 0, False, None, None, 0],  
                           ['Label', '', 12, 0, False, None, None, 0],
                           ['Label', '', 13, 0, False, None, None, 0],
                           ## Cancel, Update, Valid ################################################ 
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],   
                           ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],   
                           ## Histogram ############################################################
                           ['Graphic', '', 0, 0, False, window.HistoImageInit, None, 3],   
                           ## Rendering ############################################################
                           ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 2]]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window

    #--------------------------------------------------------------------------#
    # Filters options TAB                                                      #
    #--------------------------------------------------------------------------#
    def DisplayUpdate(self):

        # Auto updating GUI
        if self.realtimeupdateflag:                       
            self.CartoImageUpdate()
            self.HistoImageUpdate()

        # Manually updating GUI
        else:
            self.CartoImageId.setEnabled(False)  # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)  # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)  # enables the display update button


    def ApodisationFactorInit(self, id=None):
        if id is not None:
            id.setRange(0, 25)
            id.setSingleStep(5)
            id.setValue(self.apod)
        self.ApodisationFactorId = id
        return id


    def ApodisationFactorUpdate(self):
        self.apod = self.ApodisationFactorId.value()
        self.DisplayUpdate()
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MinimalValuebySpinBoxInit(self, id=None):
        self.MinValuebySpinBoxId = id
        return id


    def MinimalValuebySpinBoxReset(self):
        self.MinValuebySpinBoxId.setRange(self.zmin, self.zmax)
        self.MinValuebySpinBoxId.setValue(self.zmin)


    def MinimalValuebySpinBoxUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySpinBoxId.value()
        if (self.zmin >= self.zmax):
            self.zmin = zminsaved
        self.MinValuebySpinBoxId.setValue(self.zmin)    

        self.MinValuebySliderId.setValue(self.zmin)        
        self.DisplayUpdate()
##        if (self.realtimeupdateflag):                       
##            if (self.firstdisplayflag != True) :
##                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
##                self.HistoImageUpdate()
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MinimalValuebySliderInit(self, id=None):
        id.setOrientation(Qt.Horizontal)
        self.MinValuebySliderId = id
        return id


    def MinimalValuebySliderReset(self):
        self.MinValuebySliderId.setRange(self.zmin, self.zmax)
        self.MinValuebySliderId.setValue(self.zmin)


    def MinimalValuebySliderUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySliderId.value()
        if (self.zmin >= self.zmax):
            self.zmin = zminsaved
            self.MinValuebySliderId.setValue(self.zmin)    

        self.MinValuebySpinBoxId.setValue(self.zmin)
        
        self.DisplayUpdate()
##        if (self.realtimeupdateflag):                       
##            if (self.firstdisplayflag != True) :
##                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
##                self.HistoImageUpdate()
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySpinBoxInit(self, id=None):
        self.MaxValuebySpinBoxId = id
        return id


    def MaximalValuebySpinBoxReset(self):
        self.MaxValuebySpinBoxId.setRange(self.zmin, self.zmax)
        self.MaxValuebySpinBoxId.setValue(self.zmax)


    def MaximalValuebySpinBoxUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySpinBoxId.value()
        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved
            self.MaxValuebySpinBoxId.setValue(self.zmax)    
            
        self.MaxValuebySliderId.setValue(self.zmax)
        self.DisplayUpdate()
##        if (self.realtimeupdateflag):                       
##            if (self.firstdisplayflag != True) :
##                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
##                self.HistoImageUpdate()
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySliderInit(self, id=None):
        id.setOrientation(Qt.Horizontal)
        self.MaxValuebySliderId = id
        return id


    def MaximalValuebySliderReset(self):
        self.MaxValuebySliderId.setRange(self.zmin, self.zmax)
        self.MaxValuebySliderId.setValue(self.zmax)
        return id


    def MaximalValuebySliderUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySliderId.value()
        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved
            self.MaxValuebySliderId.setValue(self.zmax)    
            
        self.MaxValuebySpinBoxId.setValue(self.zmax)
        
        self.DisplayUpdate()
##        if (self.realtimeupdateflag):                       
##            if (self.firstdisplayflag != True) :
##                self.CartoImageUpdate()                         # updates carto only if real time updating activated and not first display
##                self.HistoImageUpdate()
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def HistoImageInit(self, id=None):
        self.histofig = None
        self.HistoImageId = id
        return id


    def HistoImageUpdate(self):
        self.histofig, _ = self.dataset.histo_plot(fig=self.histofig, zmin=self.zmin, zmax=self.zmax, cmapname=self.colormap,
                                                coloredhisto=False, cmapdisplay=True)
        self.HistoImageId.update(self.histofig)

        #histopixmap = QPixmap.grabWidget(self.histofig.canvas)   # builds the pixmap from the canvas
        #histopixmap = QPixmap.grabWidget(FigureCanvas(self.histofig))   # builds the pixmap from the canvas
        #histopixmap = histopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.HistoImageId.setPixmap(histopixmap)


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
        self.HistoImageUpdate()
        return id


    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        # processes data set
        self.dataset = self.originaldataset.copy()
        self.dataset.analyticsignal(self.apod)
        if (self.automaticrangeflag):
            self.automaticrangeflag = False
            self.zmin, self.zmax = self.dataset.histo_getlimits()            
            self.MinimalValuebySpinBoxReset()
            self.MinimalValuebySliderReset()
            self.MaximalValuebySpinBoxReset()
            self.MaximalValuebySliderReset()

        # plots geophysical image
        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.cartofig, interpolation=self.parent.interpolation, cmmin=self.zmin, cmmax=self.zmax, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)
        self.CartoImageId.update(self.cartofig)


        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
        #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))    # builds the pixmap from the canvas
        #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CartoImageId.setPixmap(cartopixmap)

        self.HistoImageUpdate()
        
        self.CartoImageId.setEnabled(True)                              # enables the carto image
        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button

        self.firstdisplayflag = False
        self.wid.setCursor(initcursor)                                  # resets the init cursor
