# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.eulerdeconvolutiondlgbox
    --------------------------------------------

    Euler deconvolution dialog box management.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
import os
import csv
import numpy as np

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

if __binding__ in ('PyQt5', 'PySide2'):
    is_qt5 = True
    is_qt4 = not is_qt5
elif __binding__ in ('PyQt4', 'PySide'):
    is_qt4 = True
    is_qt5 = not is_qt4

if is_qt4:
    from matplotlib.backends.backend_qt4agg import (
        NavigationToolbar2QT as NavigationToolbar,
        FigureCanvasQTAgg as FigureCanvas)
else:
    from matplotlib.backends.backend_qt5agg import (
        NavigationToolbar2QT as NavigationToolbar,
        FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure

from wumappy.gui.common.cartodlgbox import CartoDlgBox

from geophpy.dataset import structuralindex_getlist
import geophpy.plotting.plot as geoplot


SIZE_GRAPH_x = 440

#---------------------------------------------------------------------------#
# Euler deconvolution Dialog Box Object                                     #
#---------------------------------------------------------------------------#
class EulerDeconvolutionDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    #def new(cls, title, parent, apod=0, nflag=False, structind=0):
    def new(cls, title, parent, apod=0, nxsize=5, nysize=5, structind=None):
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
        #window.nflag = nflag
        window.structind = structind
        window.nxsize = nxsize
        window.nysize = nysize
        window.disprects = []
        window.disppoints = []
        window.xfirstpoint = None
        window.yfirstpoint = None
        window.items_list = [#
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # ELEMENT_NAME - ELEMENT_ID - COLUMN - ROW - FUNCTION_INIT - FUNCTION_UPDATE - NUM_GROUPBOX - (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN
                           #------------------------------------------------------------------------
                           ['GroupBox', 'FILTOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'RENDERING_ID', 0, 1, False, None, None, 1, 0, 1, 1, 1],
                           ['GroupBox', 'UNTITLEDGB_ID', 1, 0, False, None, None, 1, 1, 2, 2, 2],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Filter options #######################################################
                           ['Label', 'APODISATIONFACTOR_ID', 0, 0, False, None, None, 0],  
                           ['SpinBox', '', 1, 0, True, window.ApodisationFactorInit, window.ApodisationFactorUpdate, 0],    
                           #[ 'Label', 'APODISATIONFACTOR_MSG', 4, 0, False, None, None, 0],
                           ['Label', 'STRUCTINDEX_ID', 2, 0, False, None, None, 0],  
                           ['ComboBox', '', 3, 0, True, window.StructIndexValueInit, window.StructIndexValueUpdate, 0],
                           #['SpinBox', '', 5, 0, True, window.StructIndexValueInit, window.StructIndexValueUpdate, 0],
                           ['CheckBox', 'MANUAL_ID', 4, 0, True, window.ManualSubSetFlagInit, window.ManualSubSetFlagUpdate, 0], 
                           ['Label', 'FILTERNSIZE_ID', 5, 0, False, window.NSizeLabelInit, None, 0],
                           ['SpinBox', '', 6, 0, True, window.NSizeInit, window.NSizeUpdate, 0],
                           #['Label', 'FILTERNXSIZE_ID', 5, 0, False, window.NxSizeLabelInit, None, 0],
                           #['SpinBox', '', 6, 0, True, window.NxSizeInit, window.NxSizeUpdate, 0],
                           #['Label', 'FILTERNYSIZE_ID', 5, 1, False, window.NySizeLabelInit, None, 0],  
                           #['SpinBox', '', 6, 1, True, window.NySizeInit, window.NySizeUpdate, 0],    
                           #['CheckBox', 'SLIDEWINDOW_ID', 6, 0, True, window.StructIndexFlagInit, window.StructIndexFlagUpdate, 0], 
                           ['Label', 'DATASUBSET_ID', 7, 0, False, None, None, 0],   
                           ['Label', 'EULERDECONV_MSG', 8, 0, False, None, None, 0],  
                           ['TextEdit', '', 8, 0, True, window.EulerDeconvResultInit, None, 0],    
                           ['MiscButton', 'RESET_ID', 9, 0, True, window.ResetButtonInit, window.ResetButtonUpdate, 0],   
                           ['MiscButton', 'UNDO_ID', 10, 0, True, window.UndoButtonInit, window.UndoButtonUpdate, 0],      
                           ## Cancel, Update, Save ##################################################
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 2],
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 2],
                           ['MiscButton', 'SAVE_ID', 0, 2, True, window.SaveButtonInit, window.SaveButtonUpdate, 2],
                           ### Rendering ########################################################### 
                           ['Image', '', 1, 0, False, window.CartoImageInit, window.CartoImageMouseLeftClick, 1]]

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
            self.SaveButtonId.setEnabled(False)  # disables the valid button until the carto will be updated
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


##    def StructIndexValueInit(self, id=None):
##        if (id != None):
##            id.setRange(0, 3)
##            id.setSingleStep(1)
##            id.setValue(self.structind)
##        self.StructIndexValueId = id
##        return id

##    def StructIndexValueUpdate(self):
##        self.structind = self.StructIndexValueId.value()

    def StructIndexValueInit(self, id=None): 
        structind_list = structuralindex_getlist()
        #structind_list = ['-1','0', '1', '2', '3']
        try:
            structind_index = structind_list.index(self.structind)
        except:
            structind_index = 0
            
        if id is not None:
            #id.addItems(structind_list)
            # Adding comments to the SI value
            for name in structind_list:
                if name in ['-1']:
                    comment = self.asciiset.getStringValue('STRUCTINDEX-1_ID')
                    id.addItem(' '.join([name, comment]))
                elif name in ['0']:
                    comment = self.asciiset.getStringValue('STRUCTINDEX0_ID')
                    id.addItem(' '.join([name, comment]))
                elif name in ['1']:
                    comment = self.asciiset.getStringValue('STRUCTINDEX1_ID')
                    id.addItem(' '.join([name, comment]))
                elif name in ['2']:
                    comment = self.asciiset.getStringValue('STRUCTINDEX2_ID')
                    id.addItem(' '.join([name, comment]))
                elif name in ['3']:
                    comment = self.asciiset.getStringValue('STRUCTINDEX3_ID')
                    id.addItem(' '.join([name, comment]))
                else:
                    id.addItem(name)

            id.setCurrentIndex(structind_index)

        self.StructIndexValueId = id
        return id

    def StructIndexValueUpdate(self):
        text = self.StructIndexValueId.currentText().split()[0]
        if text=='-1':
            self.structind = None
        else:
            self.structind = float(text)

        manualsubsetflag = self.ManualSubsetFlagId.isChecked()
        self.CartoImageId.setEnabled(manualsubsetflag)  # enable/disable the carto to pick anomalies

##    def StructIndexFlagInit(self, id=None):
##        if (id != None):
##            id.setChecked(self.nflag)
##        self.StructIndexFlagId = id
##        self.StructIndexValueId.setEnabled(self.nflag)
##        return id
##
##
##    def StructIndexFlagUpdate(self):
##        self.nflag = self.StructIndexFlagId.isChecked()
##        self.StructIndexValueId.setEnabled(self.nflag)

    def NSizeLabelInit(self, id=None):
        if id is not None:
            id.setEnabled(not self.ManualSubsetFlagId.isChecked())
        self.NSizeLabelId = id
        return id

    def NSizeInit(self, id=None):
        if id is not None:
            id.setRange(3, 101)
            id.setSingleStep(1)
            id.setValue(self.nxsize)
            id.setEnabled(not self.ManualSubsetFlagId.isChecked())
        self.NSizeId = id
        return id

    def NSizeUpdate(self):
        self.nsize = self.NSizeId.value()
        self.DisplayUpdate()

##    def NxSizeLabelInit(self, id=None):
##        if id is not None:
##            id.setEnabled(not self.ManualSubsetFlagId.isChecked())
##        self.NxSizeLabelId = id
##        return id
##
##    def NySizeLabelInit(self, id=None):
##        if id is not None:
##            id.setEnabled(not self.ManualSubsetFlagId.isChecked())
##        self.NySizeLabelId = id
##        return id
##
##    def NxSizeInit(self, id=None):
##        if id is not None:
##            id.setRange(3, 101)
##            id.setSingleStep(1)
##            id.setValue(self.nxsize)
##            id.setEnabled(not self.ManualSubsetFlagId.isChecked())
##        self.NxSizeId = id
##        return id

##    def NxSizeUpdate(self):
##        self.nxsize = self.NxSizeId.value()
##        self.NySizeId.setValue(self.nxsize)
##        if self.square_pixel.isChecked():
##           self.NySizeId.setValue(self.nxsize)
##        self.NySizeUpdate()
##        self.DisplayUpdate()

##    def NySizeInit(self, id=None):
##        if  id is not None:
##            id.setRange(3, 101)
##            id.setSingleStep(1)
##            id.setValue(self.nysize)
##            id.setEnabled(not self.ManualSubsetFlagId.isChecked())
##        self.NySizeId = id
##        return id
##
##
##    def NySizeUpdate(self):
##        self.nysize = self.NySizeId.value()
##        self.NxSizeId.setValue(self.nysize)
##        self.DisplayUpdate()


    def ManualSubSetFlagInit(self, id=None):
        if id is not None:
            id.setChecked(True)
            self.ManualSubsetFlagId = id
        return id

    def ManualSubSetFlagUpdate(self):
        manualsubsetflag = self.ManualSubsetFlagId.isChecked()

        self.NSizeId.setEnabled(not manualsubsetflag)
        self.NSizeLabelId.setEnabled(not manualsubsetflag)

##        self.NxSizeId.setEnabled(not manualsubsetflag)
##        self.NxSizeLabelId.setEnabled(not manualsubsetflag)
##        self.NySizeId.setEnabled(not manualsubsetflag)
##        self.NySizeLabelId.setEnabled(not manualsubsetflag)

        self.DispUpdateButtonId.setEnabled(not manualsubsetflag)
        self.CartoImageId.setEnabled(manualsubsetflag)  # enable the carto to pick anomalies


    def EulerDeconvResultInit(self, id=None):
        if (id != None):
            id.setReadOnly(True)
            self.eulerdeconvresults = [['xmin','xmax','ymin','ymax','x','y','depth','n']]
            id.setText("xmin\t xmax\t ymin\t ymax | x\t y\t depth\t n")

        self.EulerDeconvResultId = id
        return id
        
    #--------------------------------------------------------------------------#
    # Reset,  button TAB                                                       #
    #--------------------------------------------------------------------------#
    def ResetResults(self):
        self.disprects = []
        self.disppoints = []
        self.eulerdeconvresults = [['xmin','xmax','ymin','ymax','x','y','depth','n']]
        self.EulerDeconvResultId.setText("xmin\t xmax\t ymin\t ymax | x\t y\t depth\t n")
        
    def ResetButtonInit(self, id=None):
        self.ResetButtonId = id
        return id

    def ResetButtonUpdate(self):
##        self.disprects=[]
##        self.disppoints=[]
##        self.eulerdeconvresults = [['xmin','xmax','ymin','ymax','x','y','depth','n']]
##        self.EulerDeconvResultId.setText("xmin\t xmax\t ymin\t ymax | x\t y\t depth\t n")
        self.ResetResults()
        self.CartoImageUpdate()                                 # updates carto image
        

    def UndoButtonInit(self, id=None):
        self.UndoButtonId = id
        return id


    def UndoButtonUpdate(self):
        self.EulerDeconvResultId.undo()
        if (len(self.disppoints) > 0):
            self.disppoints.pop()
        if (len(self.disprects) > 0):
            self.disprects.pop()
        if (len(self.eulerdeconvresults) > 1):
            self.eulerdeconvresults.pop()
        self.CartoImageUpdate()
        
    #--------------------------------------------------------------------------#
    # Cancel, Update, Save button TAB                                          #
    #--------------------------------------------------------------------------#
    def DispUpdateButtonInit(self, id=None):
        self.DispUpdateButtonId = id
        id.setHidden(self.realtimeupdateflag)                   # Hides button if real time updating activated
        id.setEnabled(not self.ManualSubsetFlagId.isChecked())  # disables the button , by default
        self.DispUpdateButtonId = id
        return id


    def DispUpdateButtonUpdate(self):
        self.CartoImageUpdate()                                 # updates carto image
        

    def SaveButtonInit(self, id=None):
        self.SaveButtonId = id
        return id


    def SaveButtonUpdate(self):
        savedir = self.configset.get('DIRECTORIES', 'eulerfiledir')

        initcursor = self.wid.cursor()                                          # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                                # sets the wait cursor

        #qfiledlg = QFileDialog(self.wid, directory=savedir)
        ###
        #filename, selectedfilter = QFileDialog.getSaveFileName(self.wid, 'Save file', dir=savedir)
        ## PyQt5's getSaveFileName has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call : 
        ## getSaveFileName(parent, caption, directory, initialFilter, selectedFilet, options)
        fullfilename = QFileDialog.getSaveFileName(self.wid, 'Save file', savedir)

        # File selected (empty (False) if cancel is clicked)
        if filename:
            self.configset.set('DIRECTORIES', 'eulerfiledir', os.path.dirname(filename))
            # formatting results
            csvtosave = [self.eulerdeconvresults[0]]  # Headers
            for row in self.eulerdeconvresults[1:]:
                csvtosave.append(["%0.2f" % v for v in row])

            # saving to a file
            with open(filename, 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter='\t')
                writer.writerows(csvtosave)

        ###
##        qfiledlg = QFileDialog(self.wid, directory=savedir)
##        qfiledlg.setFont(self.asciiset.font)
##        qfiledlg.setGeometry(self.wid.geometry().left(), self.wid.geometry().top(), qfiledlg.geometry().width(), qfiledlg.geometry().height())
##        qfiledlg.setAcceptMode(QFileDialog.AcceptSave)
##        qfiledlg.show()
##        qfiledlg.exec()
##        if (qfiledlg.result() == QDialog.Accepted):
##            fullfilename = qfiledlg.selectedFiles()
##            self.configset.set('DIRECTORIES', 'eulerfiledir', os.path.dirname(fullfilename[0]))
##            with open(fullfilename[0], 'w') as csvfile:
##                writer = csv.writer(csvfile, delimiter='\t')
##                writer.writerows(self.eulerdeconvresults)

        self.wid.setCursor(initcursor)                                          # resets the init cursor
        self.SaveButtonId.setEnabled(False)                                     # disables the save button
        

    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id


    def CartoImageInit(self, id=None):
        self.cartofig = None
        self.CartoImageId = id
        self.CartoImageUpdate()
        return id


    def CartoImageMouseLeftClick(self, x=None, y=None):
        if x is not None and y is not None and self.ManualSubsetFlagId.isChecked():
            if (self.xfirstpoint==None or self.yfirstpoint==None):
                # first point of rectangle to save
                self.xfirstpoint = x
                self.yfirstpoint = y
            else:
                # second point of rectangle to construct the rectangle
                if (x < self.xfirstpoint):
                    xmin = x
                    xmax = self.xfirstpoint
                else:
                    xmin = self.xfirstpoint
                    xmax = x
                if (y < self.yfirstpoint):
                    ymin = y
                    ymax = self.yfirstpoint
                else:
                    ymin = self.yfirstpoint
                    ymax = y
                self.disprects.append([xmin, ymin, xmax - xmin, ymax - ymin])
                #self.structind, x, y, depth, xnearestmin, ynearestmin, xnearestmax, ynearestmax = self.dataset.eulerdeconvolution(xmin, xmax, ymin, ymax, self.apod, self.nflag, self.structind)
                x, y, depth, self.structind, residuals, xnearestmin, xnearestmax, ynearestmin, ynearestmax = self.dataset.eulerdeconvolution(windows=[xmin, xmax, ymin, ymax],  apod=self.apod, structind=self.structind)[0]
                
                self.disppoints.append([x, y])
                self.eulerdeconvresults.append([xnearestmin,xnearestmax,ynearestmin,ynearestmax,x,y,depth,self.structind])
                self.EulerDeconvResultId.append("%.02f\t %.02f\t %.02f\t %.02f | %.02f\t %.02f\t %.02f\t %.02f"%(xnearestmin,xnearestmax,ynearestmin,ynearestmax,x,y,depth,self.structind))
                self.CartoImageUpdate()
                self.xfirstpoint = None
                self.yfirstpoint = None
            

    def CartoImageUpdate(self):
        initcursor = self.wid.cursor()                                  # saves the init cursor type
        self.wid.setCursor(Qt.WaitCursor)                        # sets the wait cursor

        # processes data set
        self.dataset = self.originaldataset.copy()

        ## Ploting geophysical image #################################
##        # Classic display
##        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype,
##                                                     self.parent.colormap,
##                                                     creversed=self.parent.reverseflag,
##                                                     fig=self.cartofig,
##                                                     interpolation=self.parent.interpolation,
##                                                     cmmin=self.parent.zmin,
##                                                     cmmax=self.parent.zmax,
##                                                     cmapdisplay = False,
##                                                     axisdisplay = False,
##                                                     logscale=self.parent.colorbarlogscaleflag,
##                                                     rects = self.disprects,
##                                                     points = self.disppoints)
##        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
##        cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))    # builds the pixmap from the canvas

        ## Automatic sub-windows euler deconvolution ###########################
        if not self.ManualSubsetFlagId.isChecked():
            self.ResetResults()
            #self.disppoints = []
            #self.disprects = []
            #self.eulerdeconvresults = []
            xstep = self.NSizeId.value()
            ystep = self.NSizeId.value()

            results = self.dataset.eulerdeconvolution(apod=self.apod, structind=self.structind, xstep=xstep, ystep=ystep)
            window_extents = np.asarray(results)[:,5:].tolist()  # Euler sub-windows extents
            self.disprects = geoplot.extents2rectangles(window_extents)  # Sub-windows extents to rectangle to be plot

            for result in results:
                x, y, depth, structind, residuals, xnearestmin, xnearestmax, ynearestmin, ynearestmax = result
                self.disppoints.append([x, y])
                self.eulerdeconvresults.append([xnearestmin, xnearestmax,
                                                ynearestmin, ynearestmax,
                                                x, y, depth, structind])

                self.EulerDeconvResultId.append("%.02f\t %.02f\t %.02f\t %.02f | %.02f\t %.02f\t %.02f\t %.02f" %(xnearestmin, xnearestmax, ynearestmin,
                                                                                    ynearestmax, x, y, depth, structind))

        # Bigger display
        tempfilename=self.configset.temp_dir + "/temp.PNG"
        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype,
                                                     self.parent.colormap,
                                                     creversed=self.parent.reverseflag,
                                                     fig=self.cartofig,
                                                     filename=tempfilename,
                                                     interpolation=self.parent.interpolation,
                                                     cmmin=self.parent.zmin,
                                                     cmmax=self.parent.zmax,
                                                     cmapdisplay = False,
                                                     axisdisplay = False,
                                                     labeldisplay = False,
                                                     logscale=self.parent.colorbarlogscaleflag,
                                                     rects = self.disprects,
                                                     points=self.disppoints
                                                      )
        cartopixmap = QPixmap(tempfilename)

        ## Scaling pixmap image ######################################
        # Scaling pixmap to total widget width&height so that
        # mouse position on pixmap = mouse position on widget
        
##        cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        w, h = self.CartoImageId.getSize()
        cartopixmap.scaled(w, h)
        
        self.CartoImageId.setPixmap(cartopixmap) 
        self.CartoImageId.setEnabled(True)                              # enables the carto image
        if (len(self.eulerdeconvresults) > 1):
            self.ResetButtonId.setEnabled(True)                         # enables the reset button
            self.UndoButtonId.setEnabled(True)                          # enables the undo button
            self.SaveButtonId.setEnabled(True)                          # enables the save button
        else:
            self.ResetButtonId.setEnabled(False)                         # disables the reset button
            self.UndoButtonId.setEnabled(False)                          # disables the undo button
            self.SaveButtonId.setEnabled(False)                          # disables the save button
            
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button
        
        self.wid.setCursor(initcursor)                                  # resets the init cursor
