# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.festoonfiltdlgbox
    -------------------------------------

    Festoon filtering dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''
from __future__ import absolute_import

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

from wumappy.gui.common.cartodlgbox import CartoDlgBox

from geophpy.dataset import festooncorrelation_getlist
#---------------------------------------------------------------------------#
# Festoon Filtering Dialog Box Object                                       #
#---------------------------------------------------------------------------#
class FestoonFiltDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent, method='Crosscorr', shift=0, corrmin=0.4, uniformshift=False):
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
        window.method = method
        window.shift = shift
        window.corrmin = corrmin
        window.uniformshift = uniformshift
        window.items_list = [#
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # ELEMENT_NAME - ELEMENT_ID - COLUMN - ROW - FUNCTION_INIT - FUNCTION_UPDATE - NUM_GROUPBOX - (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN
                           #------------------------------------------------------------------------
                           ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'RENDERING_ID', 0, 1, False, None, None, 1, 0, 1, 1, 1],
                           ['GroupBox', 'CORRELATIONMAP_ID', 0, 2, False, None, None, 2, 0, 1, 1, 1],
                           ['GroupBox', 'CORRELATIONSUM_ID', 0, 3, False, None, None, 3, 0, 1, 1, 1],
                           ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 1, 1, 4, 2],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Filter options #######################################################
                           ['Label','FLTERRANGE_ID', 0, 0, False, None, None, 0, 1, 4],
                           ['Label', 'MINIMALVALUE_ID', 1, 0, False, None, None, 0],
                           ['DoubleSpinBox', '', 1, 3, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 0],
                           ['Slider', '', 1, 1, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 0, 1, 2],
                           ['Label', 'MAXIMALVALUE_ID', 2, 0, False, None, None, 0],
                           ['DoubleSpinBox', '', 2, 3, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 0],
                           ['Slider', '', 2, 1, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 0, 1, 2],
                           ['Label', '', 3, 0, False, None, None, 0],
                           ['Label', 'FESTOONFILTMETHOD_ID', 4, 0, False, None, None, 0],
                           ['ComboBox', '', 5, 0, True, window.MethodInit, window.MethodUpdate, 0, 1, 4],
                           ['Label', '', 5, 1, False, None, None, 0],
                           ['Label', '', 6, 0, False, None, None, 0],
                           ['CheckBox', 'FESTOONFILTSHIFT_ID', 7, 0, False, window.UniformShiftInit, window.UniformShiftUpdate, 0],
                           ['SpinBox', '', 8, 0, True, window.ShiftInit, window.ShiftUpdate, 0, 1, 4],
                           ['Label', '', 9, 0, False, None, None, 0],
                           ['Label', 'FESTOONFILTMINCORR_ID', 10, 0, False, None, None, 0, 1, 4],
                           ['DoubleSpinBox', '', 11, 0, True, window.CorrMinInit, window.CorrMinUpdate, 0, 1, 4],
                           ['Label', '', 12, 0, False, None, None, 0],
                           ['Label', '', 13, 0, False, None, None, 0],
                           ## Correlation Map ###################################################### 
                           ['Graphic', '', 7, 0, False, window.CorrMapImageInit, None, 2],   
                           ## Correlation Sum ######################################################
                           ['Graphic', '', 9, 0, False, window.CorrSumImageInit, None, 3],   
                           ## Cancel, Update, Valid ################################################
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 4],   
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 4],   
                           ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 4],   
                           ### Rendering ########################################################### 
                           ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 1]]

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
            self.CorrSumImageUpdate()
            self.CorrMapImageUpdate()

        # Manually updating GUI
        else:
            self.CartoImageId.setEnabled(False)  # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)  # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)  # enables the display update button


    def MinimalValuebySpinBoxInit(self, id=None):
        if id is not None:
            # data limits from  histogram
            zmin, zmax = self.dataset.histo_getlimits()  

            id.setRange(zmin, zmax)
            id.setValue(self.zmin)

        self.MinValuebySpinBoxId = id
        return id


    def MinimalValuebySpinBoxUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySpinBoxId.value()

        if (self.zmin >= self.zmax):
            self.zmin = zminsaved

        self.MinValuebySpinBoxId.setValue(self.zmin)    
        self.MinValuebySliderId.setValue(self.zmin)
        self.DisplayUpdate()

##        #self.HistoImageUpdate()
##
##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Manual update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MinimalValuebySliderInit(self, id=None):
        if id is not None:
            # data limits from  histogram
            zmin, zmax = self.dataset.histo_getlimits()

            id.setOrientation(Qt.Horizontal)
            id.setRange(zmin, zmax)
            id.setValue(self.zmin)

        self.MinValuebySliderId = id
        return id


    def MinimalValuebySliderUpdate(self):
        zminsaved = self.zmin
        self.zmin = self.MinValuebySliderId.value()

        if (self.zmin >= self.zmax):
            self.zmin = zminsaved

        self.MinValuebySliderId.setValue(self.zmin)
        self.MinValuebySpinBoxId.setValue(self.zmin)
        self.DisplayUpdate()

##        #self.HistoImageUpdate()
##
##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Manual update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySpinBoxInit(self, id=None):
        if id is not None:
            # data limits from  histogram
            zmin, zmax = self.dataset.histo_getlimits()

            id.setRange(zmin, zmax)
            id.setValue(self.zmax)

        self.MaxValuebySpinBoxId = id
        return id


    def MaximalValuebySpinBoxUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySpinBoxId.value()
        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved

        self.MaxValuebySpinBoxId.setValue(self.zmax)    
        self.MaxValuebySliderId.setValue(self.zmax)
        self.DisplayUpdate()

##        #self.HistoImageUpdate()
##
##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Manual update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySliderInit(self, id=None):
        if id is not None:
            # data limits from  histogram
            zmin, zmax = self.dataset.histo_getlimits()

            id.setOrientation(Qt.Horizontal)
            id.setRange(zmin, zmax)
            id.setValue(self.zmax)

        self.MaxValuebySliderId = id
        return id


    def MaximalValuebySliderUpdate(self):
        zmaxsaved = self.zmax
        self.zmax = self.MaxValuebySliderId.value()

        if (self.zmax <= self.zmin):
            self.zmax = zmaxsaved

        self.MaxValuebySliderId.setValue(self.zmax)
        self.MaxValuebySpinBoxId.setValue(self.zmax)
        self.DisplayUpdate()

##        #self.HistoImageUpdate()
##
##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Manual update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MethodInit(self, id=None):                                                  
        method_list = festooncorrelation_getlist()
        try:
            method_index = method_list.index(self.method)
        except:
            method_index = 0
            
        if id is not None:
            #id.addItems(method_list)
            # Adding speed execution comments to the method 
            for name in method_list:
                if name in ['Crosscorr']:
                    id.addItem(' '.join([name, '(Fast)']))
                elif name in ['Pearson']:
                    id.addItem(' '.join([name, '(Slow)']))
                elif name in ['Kendall', 'Spearman']:
                    id.addItem(' '.join([name, '(Extra-slow)']))
                else:
                    id.addItem(name)

            id.setCurrentIndex(method_index)
        self.MethodId = id
        return id


    def MethodUpdate(self):
        # self.method = self.MethodId.currentText()
        text = self.MethodId.currentText()
        method_list = festooncorrelation_getlist()

        index_bool = [element in text  for element in method_list]
        method_index = index_bool.index(True)

        self.method = method_list[method_index]

        self.DisplayUpdate()

##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Manual update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def UniformShiftInit(self, id=None):
        if id is not None:
            id.setChecked(self.uniformshift)
        self.UniformShiftId = id
        return id

  
    def UniformShiftUpdate(self):
        self.uniformshift = self.UniformShiftId.isChecked()  # updates Uniform Shift Flag
        self.ShiftId.setEnabled(self.uniformshift)           # disables/enables Uniform Shift Value
        self.DisplayUpdate()

##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Manual update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def ShiftInit(self, id=None):
        if id is not None:
            shiftrange = (self.dataset.info.y_max - self.dataset.info.y_min)/2
            id.setRange(-shiftrange, +shiftrange)
            id.setValue(self.shift)
        self.ShiftId = id
        self.ShiftId.setEnabled(self.uniformshift)
        return id


    def ShiftUpdate(self):
        self.shift = self.ShiftId.value()
        self.DisplayUpdate()

##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Auto update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def CorrMinInit(self, id=None):
        if id is not None:
            id.setRange(0, 1.0)
            id.setSingleStep(0.1)
            id.setValue(self.corrmin)
        self.CorrMinId = id
        return id

    def CorrMinUpdate(self):
        self.corrmin = self.CorrMinId.value()
        self.DisplayUpdate()

##        # Auto update GUI
##        if (self.realtimeupdateflag):                       
##            self.CartoImageUpdate()                             # updates carto only if real time updating activated
##
##        # Auto update GUI
##        else:
##            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
##            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
##            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    #--------------------------------------------------------------------------#
    # Correlation Map TAB                                                      #
    #--------------------------------------------------------------------------#
    def CorrMapImageInit(self, id=None):
        self.CorrMapImageId = id
        self.corrmapfig = None
        self.CorrMapImageUpdate()
        return id

    def CorrMapImageUpdate(self):
        self.corrmapfig = self.dataset.correlation_plotmap(fig=self.corrmapfig, method=self.method)
        self.CorrMapImageId.update(self.corrmapfig)

        #pixmap = QPixmap.grabWidget(self.corrmapfig.canvas)   # builds the pixmap from the canvas
        #pixmap = QPixmap.grabWidget(FigureCanvas(self.corrmapfig))   # builds the pixmap from the canvas
        #pixmap = pixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CorrMapImageId.setPixmap(pixmap)

    #--------------------------------------------------------------------------#
    # Correlation Sum TAB                                                      #
    #--------------------------------------------------------------------------#
    def CorrSumImageInit(self, id=None):
        self.CorrSumImageId = id
        self.corrsumfig = None
        self.CorrSumImageUpdate()
        return id

    def CorrSumImageUpdate(self):
        self.corrsumfig = self.dataset.correlation_plotsum(fig=self.corrsumfig, method=self.method)
        self.CorrSumImageId.update(self.corrsumfig)

        #pixmap = QPixmap.grabWidget(self.corrsumfig.canvas)   # builds the pixmap from the canvas
        #pixmap = QPixmap.grabWidget(FigureCanvas(self.corrsumfig))   # builds the pixmap from the canvas
        #pixmap = pixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CorrSumImageId.setPixmap(pixmap)

    #--------------------------------------------------------------------------#
    # Rendering TAB                                                            #
    #--------------------------------------------------------------------------#
    def CartoImageInit(self, id=None):
        self.cartofig = None
        self.CartoImageId = id
        self.CartoImageUpdate()
        return id

    def CartoImageUpdate(self):
        # Loading cursor
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        # Processing dataset
        self.dataset = self.originaldataset.copy()
        self.shift = self.dataset.festoonfilt(method=self.method, shift=self.shift, corrmin=self.corrmin, uniformshift=self.uniformshift,
                                              setmin=self.zmin, setmax=self.zmax)

        # Plot geophysical image
        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.cartofig, interpolation=self.parent.interpolation, cmmin=self.zmin, cmmax=self.zmax, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)
        self.CartoImageId.update(self.cartofig)

        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
        #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))    # builds the pixmap from the canvas
        #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CartoImageId.setPixmap(cartopixmap)
        
        # Updating dependencies
        #self.CorrSumImageUpdate()
        #self.CorrMapImageUpdate()
        self.ShiftId.setValue(self.shift)

        # Enabling Map & Buttons
        self.CartoImageId.setEnabled(True)                              # enables the carto image
        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button

        # Resets the init cursor
        self.wid.setCursor(initcursor)                                    

    #--------------------------------------------------------------------------#
    # Cancel, Update, Valid button TAB                                         #
    #--------------------------------------------------------------------------#    
    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)       # Hides button if real time updating activated
        id.setEnabled(False)                        # disables the button , by default
        return id


    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()
        self.CorrSumImageUpdate()
        self.CorrMapImageUpdate()
        

    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id


    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id
