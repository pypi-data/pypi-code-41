# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.constdestripdlgbox
    --------------------------------------

    Constant destriping dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
from geophpy.dataset import (
    destriping_getlist,
    destripingconfig_getlist,
    destripingreference_getlist)

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
# Constant Destriping Dialog Box Object                                     #
#---------------------------------------------------------------------------#
class ConstDestripDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent,
            nprof=0, method='additive', reference='mean', config='mono'):
        '''
        '''
        
        window = cls()
        window.parent = parent
        window.dataset = parent.dataset
        window.colormap = parent.dataset.info.cmapname
        window.originaldataset = parent.dataset
        window.rawdataset = parent.dataset  # for display before filter
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.zmin = window.parent.zmin
        window.zmax = window.parent.zmax
        zmin, zmax = window.dataset.histo_getlimits()
        if (window.zmin == None):
            window.zmin = zmin
        if (window.zmax == None):
            window.zmax = zmax            

        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')
        window.nprof = nprof
        window.method = method
        window.config = config
        window.reference = reference
        window.items_list = [#
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # ELEMENT_NAME - ELEMENT_ID - COLUMN - ROW - FUNCTION_INIT - FUNCTION_UPDATE - NUM_GROUPBOX - (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN
                           #------------------------------------------------------------------------
                           ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'RENDERING_ID', 0, 2, False, None, None, 0, 1, 1, 1, 1],
                           ['GroupBox', 'HISTOGRAM_ID', 0, 1, False, None, None, 0, 2, 1, 1, 1],
                           ['GroupBox', 'PROFILESMEAN_ID', 0, 3, False, None, None, 0, 3, 1, 1, 1],
                           ['GroupBox', 'UNTITLEDGB_ID', 2, 0, False, None, None, 1, 0, 1, 4, 2],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Filter options #######################################################
                           ['Label', 'PROFILESNB_ID', 0, 0, False, None, None, 0, 1, 0],
                           #['SpinBox', '', 1, 0, True, window.ProfilesNbInit, window.ProfilesNbUpdate, 0],
                           ['ComboBox', '', 1, 0, True, window.ProfilesNbInit, window.ProfilesNbUpdate, 0, 1, 0],
                           ['Label', '', 2, 0, False, None, None, 0],
                           ['Label','FLTERRANGE_ID', 3, 0, False, None, None, 0, 1, 0],
                           ['Label', 'MINIMALVALUE_ID', 4, 0, False, None, None, 0],  
                           ['DoubleSpinBox', '', 4, 3, True, window.MinimalValuebySpinBoxInit, window.MinimalValuebySpinBoxUpdate, 0],    
                           ['Slider', '', 4, 1, True, window.MinimalValuebySliderInit, window.MinimalValuebySliderUpdate, 0, 1, 2],  
                           ['Label', 'MAXIMALVALUE_ID', 5, 0, False, None, None, 0],  
                           ['DoubleSpinBox', '', 5, 3, True, window.MaximalValuebySpinBoxInit, window.MaximalValuebySpinBoxUpdate, 0],    
                           ['Slider', '', 5, 1, True, window.MaximalValuebySliderInit, window.MaximalValuebySliderUpdate, 0, 1, 2],
                           ['Label', '', 6, 0, False, None, None, 0],
                           ['Label', 'DESTRIPINGMETHOD_ID', 7, 0, False, None, None, 0, 1, 0, 1, 0],  
                           ['ComboBox', '', 8, 0, True, window.MethodInit, window.MethodUpdate, 0, 1, 0],   
                           ['Label', 'CONFIGDESTRIP_ID', 9, 0, False, None, None, 0, 1, 0],  
                           ['ComboBox', '', 10, 0, True, window.ConfigInit, window.ConfigUpdate, 0, 1, 0],    
                           ['Label', 'REF_ID', 11, 0, False, None, None, 0, 1, 0],  
                           ['ComboBox', '', 12, 0, True, window.ReferenceInit, window.ReferenceUpdate, 0, 1, 0], 
                           ['Label', '', 13, 0, False, None, None, 0],   
                           ## Cancel, Update, Valid ################################################ 
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 4],   
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 4],   
                           ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 4],   
                           ### Histogram ########################################################### 
                           ['Graphic', '', 6, 0, False, window.HistoImageInit, None, 2],
                           ## Mean cross-track profile ############################################# 
                           ['Graphic', '', 6, 0, False, window.ProfMeanImageInit, None, 3],
                           ## RenderingRendering ###################################################
                           ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 1]]

        dlgbox = CartoDlgBox(title, window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window


    #--------------------------------------------------------------------------#
    # Filters options TAB                                                      #
    #--------------------------------------------------------------------------#
    def ProfilesNbInit(self, id=None):
        minval, maxval = 1, len(self.dataset.data.z_image.T)
        profilelist = ['0', 'all'] +  [str(i) for i in range(minval, maxval+1)]
        id.addItems(profilelist)
        
        try:
            index = id.findText('all')
            self.nprof = 'all'
        except:
            index = 0
            self.nprof = 0

        id.setCurrentIndex(index)

        ## Forcing max visible item
        # new StyleSheet is used
        id.setStyleSheet("QComboBox { combobox-popup: 0; }")
        id.setMaxVisibleItems(10)

        # the scroll bar has to be added manually
        id.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ProfilesNbId = id
        
        return id


    def ProfilesNbUpdate(self):
        
        if self.ProfilesNbId.currentText()=='all':
            self.nprof = self.ProfilesNbId.currentText()
        else:
            self.nprof = int(self.ProfilesNbId.currentText())

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MinimalValuebySpinBoxInit(self, id=None):
        if (id != None):                                                    
            zmin, zmax = self.dataset.histo_getlimits()         # gets the limits of the histogram of the data set
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
        #self.HistoImageUpdate()

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MinimalValuebySliderInit(self, id=None):
        if (id != None):
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
        #self.HistoImageUpdate()

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySpinBoxInit(self, id=None):
        if (id != None):
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
        #self.HistoImageUpdate()

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MaximalValuebySliderInit(self, id=None):
        if (id != None):
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
        #self.HistoImageUpdate()

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def MethodInit(self, id=None):
        list = destriping_getlist()
        id.addItems(list)
        try:
            index = id.findText(self.method)
        except:
            index = 0
        id.setCurrentIndex(index)
        self.MethodId = id
        return id


    def MethodUpdate(self):
        self.method = self.MethodId.currentText()

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def ConfigInit(self, id=None):
        list = destripingconfig_getlist()
        id.addItems(list)
        try:
            index = id.findText(self.config)
        except:
            index = 0
        id.setCurrentIndex(index)
        self.ConfigId = id
        return id


    def ConfigUpdate(self):
        self.config = self.ConfigId.currentText()

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def ReferenceInit(self, id=None):
        list = destripingreference_getlist()
        id.addItems(list)
        try:
            index = id.findText(self.reference)
        except:
            index = 0
        id.setCurrentIndex(index)
        self.ReferenceId = id
        return id


    def ReferenceUpdate(self):
        self.reference = self.ReferenceId.currentText()

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    #--------------------------------------------------------------------------#
    # Cancel, Update, Valid button TAB                                         #
    #--------------------------------------------------------------------------#
    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)       # Hides button if real time updating activated
        id.setEnabled(False)                        # disables the button , by default
        return id


    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                     # updates carto image
        self.ProfMeanImageUpdate()
        self.HistoImageUpdate()


    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id


    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id


    #--------------------------------------------------------------------------#
    # Mean cross-track profile TAB                                             #
    #--------------------------------------------------------------------------#
    def ProfMeanImageInit(self, id=None):
        self.profmeanfig = None
        self.ProfMeanImageId = id
        self.ProfMeanImageUpdate()
        return id

    
    def ProfMeanImageUpdate(self, id=None):
        self.profmeanfig = self.rawdataset.meantrack_plot(fig=self.profmeanfig, Nprof=self.nprof, setmin=self.zmin, setmax=self.zmax,
                                                          method=self.method, reference=self.reference, config=self.config, plotflag='both') # using  dataset to display before/after filter
        self.ProfMeanImageId.update(self.profmeanfig)

        #pixmap = QPixmap.grabWidget(FigureCanvas(self.profmeanfig))   # builds the pixmap from the canvas
        #pixmap = pixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.ProfMeanImageId.setPixmap(pixmap)


    #--------------------------------------------------------------------------#
    # Histogram TAB                                                            #
    #--------------------------------------------------------------------------#
    def HistoImageInit(self, id=None):
        self.HistoImageId = id
        return id


    def HistoImageUpdate(self):
        self.histofig, _ = self.dataset.histo_plot(zmin=self.zmin, zmax=self.zmax, cmapname= self.colormap)
        self.HistoImageId.update(self.histofig)

        #histopixmap = QPixmap.grabWidget(self.histofig.canvas)   # builds the pixmap from the canvas
        #histopixmap = QPixmap.grabWidget(FigureCanvas(self.histofig))   # builds the pixmap from the canvas
        #histopixmap = histopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.HistoImageId.setPixmap(histopixmap)


    #--------------------------------------------------------------------------#
    # Rendering TAB                                                            #
    #--------------------------------------------------------------------------#
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
        self.dataset.destripecon(Nprof=self.nprof, setmin=self.zmin, setmax=self.zmax, method=self.method, reference=self.reference, config=self.config)

        # plots geophysical image
        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype, self.parent.colormap, creversed=self.parent.reverseflag, fig=self.cartofig, interpolation=self.parent.interpolation, cmmin=self.zmin, cmmax=self.zmax, cmapdisplay = True, axisdisplay = True, logscale=self.parent.colorbarlogscaleflag)
        self.CartoImageId.update(self.cartofig)

        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
        #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))    # builds the pixmap from the canvas
        #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CartoImageId.setPixmap(cartopixmap)

        self.CartoImageId.setEnabled(True)                              # enables the carto image
        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button

        self.wid.setCursor(initcursor)                                  # resets the init cursor
        
