# -*- coding: utf-8 -*-
'''
    wumappy.gui.dataset.transformdlgbox
    --------------------------------------

    Data Set transformations dialog box management.

    :copyright: Copyright 2018-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.
'''

from __future__ import absolute_import

from geophpy.dataset import *

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
#from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

import numexpr as ne

from wumappy.gui.common.cartodlgbox import CartoDlgBox

#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure

#SIZE_GRAPH_x = 440

#---------------------------------------------------------------------------#
# Transform Dialog Box Object                                               #
#---------------------------------------------------------------------------#
class DatasetTransformDlgBox:
    
    def __init__(self):
        pass

    @classmethod
    def new(cls, title, parent):
        '''
        '''
        
        window = cls()
        window.title = title
        window.parent = parent
        window.dataset = parent.dataset
        window.originaldataset = parent.dataset
        window.parentid = parent.wid
        window.asciiset = parent.asciiset
        window.configset = parent.configset
        window.icon = parent.icon
        window.realtimeupdateflag = window.configset.getboolean('MISC', 'realtimeupdateflag')                                                                
        window.items_list = [
                           #------------------------------------------------------------------------
                           ## GroupBox Properties
                           # TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ORIENTATION (0=Vert, 1=Horiz), ROW_SPAN, COL_SPAN, GROUP_TAB_TYPE
                           #------------------------------------------------------------------------
                           ['GroupBox', 'TRANSFORM_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],
                           ['GroupBox', 'UNTITLEDGB_ID', 1, 0, False, None, None, 2, 1, 1, 3, 2],
                           ['GroupBox', 'RENDERING_ID', 0, 2, False, None, None, 1, 0, 1, 1, 1],
                           #------------------------------------------------------------------------
                           ## Other elements properties
                           # [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]
                           #------------------------------------------------------------------------
                           ## Transform options TAB ################################################
                           ['Label', 'TRANSLATION_ID', 0, 0, False, None, None, 0],
                           ['Label', 'XOFFSET_ID', 1, 0, False, None, None, 0],
                           ['LineEdit', '', 1, 1, True, window.XoffsetValueInit, window.XoffsetValueUpdate, 0],
                           ['Label', 'YOFFSET_ID', 2, 0, False, None, None, 0],
                           ['LineEdit', '', 2, 1, True, window.YoffsetValueInit, window.YoffsetValueUpdate, 0],
                           ['Label', '', 3, 0, False, None, None, 0],
                           ['Label', 'ROTATION_ID', 4, 0, False, None, None, 0],
                           ['Label', 'ANGLE_ID', 5, 0, False, None, None, 0],
                           ['ComboBox', '', 5, 1, True, window.RotAngleInit, window.RotAngleUpdate, 0],
                           ['Label', '', 6, 0, False, None, None, 0],
                           ['Label', 'SCALING_ID', 7, 0, False, None, None, 0],
                           ['Label', 'XSCALE_ID', 8, 0, False, None, None, 0],
                           ['LineEdit', '', 8, 1, True, window.XscaleValueInit, window.XscaleValueUpdate, 0],
                           ['Label', 'YSCALE_ID', 9, 0, False, None, None, 0],
                           ['LineEdit', '', 9, 1, True, window.YscaleValueInit, window.YscaleValueUpdate, 0],
                           ['Label', '', 10, 0, False, None, None, 0],
                           ## Cancel, Update Valid #################################################
                           ['CancelButton', 'CANCEL_ID', 0, 0, True, window.CancelButtonInit, None, 1],
                           ['MiscButton', 'DISPUPDATE_ID', 0, 1, True, window.DispUpdateButtonInit, window.DispUpdateButtonUpdate, 1],
                           ['ValidButton', 'VALID_ID', 0, 2, True, window.ValidButtonInit, None, 1],
                           ### Rendering TAB #######################################################
                           ['Graphic', '', 0, 1, False, window.CartoImageInit, None, 2]]
                           #['Image', '', 0, 1, False, window.CartoImageInit, None, 2]]

        dlgbox = CartoDlgBox(window.asciiset.getStringValue('TRANSFORM_ID'), window, window.items_list)
        dlgbox.exec()

        return dlgbox.result(), window


    #--------------------------------------------------------------------------#
    # Transform options TAB                                                    #
    #--------------------------------------------------------------------------#
    def XoffsetValueInit(self, id=None):
        if id is not None:
            id.setText(str(0))

        self.XoffsetValueId = id
        self.xoffset = 0
        return id


    def XoffsetValueUpdate(self):
        try:
            self.xoffset =  ne.evaluate(self.XoffsetValueId.text())
            self.XoffsetValueId.setText(str(self.xoffset))
        except:
            self.xoffset = 0
            self.XoffsetValueId.setText('0')

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def YoffsetValueInit(self, id=None):
        if id is not None:
            id.setText(str(0))

        self.YoffsetValueId = id
        self.yoffset = 0
        return id


    def YoffsetValueUpdate(self):
        try:
            self.yoffset =  ne.evaluate(self.YoffsetValueId.text())
            self.YoffsetValueId.setText(str(self.yoffset))
        except:
            self.yoffset = 0
            self.YoffsetValueId.setText('0')

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def RotAngleInit(self, id=None):
        angle_list = [str(i) for i in rotation_angle_getlist()]
        angle_index = 0
        
        if id is not None:
            id.addItems(angle_list)
            id.setCurrentIndex(angle_index)

        self.RotAngleId = id
        self.angle = float(self.RotAngleId.currentText())
        return id


    def RotAngleUpdate(self):
        self.angle = float(self.RotAngleId.currentText())        

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def XscaleValueInit(self, id=None):
        if id is not None:
            id.setText(str(1))

        self.XscaleValueId = id
        self.xscale = 1
        self.XscaleValueId.setEnabled(False)
        return id


    def XscaleValueUpdate(self):
        try:
            self.xscale =  ne.evaluate(self.XscaleValueId.text())
            self.XscaleValueId.setText(str(self.xscale))
        except:
            self.xscale = 1
            self.XscaleValueId.setText('1')

        # Auto update GUI
        if (self.realtimeupdateflag):                       
            self.CartoImageUpdate()                             # updates carto only if real time updating activated

        # Manual update GUI
        else:
            self.CartoImageId.setEnabled(False)                 # disables the carto image to indicate that carto not still updated
            self.ValidButtonId.setEnabled(False)                # disables the valid button until the carto will be updated
            self.DispUpdateButtonId.setEnabled(True)            # enables the display update button


    def YscaleValueInit(self, id=None):
        if id is not None:
            id.setText(str(1))

        self.YscaleValueId = id
        self.yscale = 1
        self.YscaleValueId.setEnabled(False)
        return id


    def YscaleValueUpdate(self):
        try:
            self.yscale =  ne.evaluate(self.YscaleValueId.text())
            self.YscaleValueId.setText(str(self.yscale))
        except:
            self.yscale = 1
            self.YscaleValueId.setText('1')

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


    def ValidButtonInit(self, id=None):
        self.ValidButtonId = id
        return id


    def CancelButtonInit(self, id=None):
        self.CancelButtonId = id
        return id


    #--------------------------------------------------------------------------#
    # Rendering TAB                                                            #
    #--------------------------------------------------------------------------#
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
        self.dataset.rotate(angle=self.angle)
        self.dataset.translate(shiftx=self.xoffset, shifty=self.yoffset)

        # plots geophysical image
        self.cartofig, cartocmap = self.dataset.plot(self.parent.plottype, self.parent.colormap,
                                                     creversed=self.parent.reverseflag, fig=self.cartofig,
                                                     interpolation=self.parent.interpolation,
                                                     cmmin=self.parent.zmin, cmmax=self.parent.zmax,
                                                     cmapdisplay = self.parent.colorbardisplayflag,
                                                     axisdisplay = self.parent.axisdisplayflag,
                                                     logscale=self.parent.colorbarlogscaleflag)

        #self.cartofig.patch.set_alpha(0.1)  # transparent figure background
        #self.cartofig.patch.set_linewidth(2)
        #self.cartofig.patch.set_edgecolor('black')
        self.CartoImageId.update(self.cartofig)
            
        #cartopixmap = QPixmap.grabWidget(self.cartofig.canvas)    # builds the pixmap from the canvas
        #cartopixmap = QPixmap.grabWidget(FigureCanvas(self.cartofig))
        #cartopixmap = cartopixmap.scaledToWidth(SIZE_GRAPH_x)
        #self.CartoImageId.setPixmap(cartopixmap)
        self.CartoImageId.setEnabled(True)                              # enables the carto image
        self.ValidButtonId.setEnabled(True)                             # enables the valid button
        self.DispUpdateButtonId.setEnabled(False)                       # disables the display update button
        
        self.wid.setCursor(initcursor)                                  # resets the init cursor
