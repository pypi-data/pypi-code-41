import wx
import math
from wx.lib.pubsub import pub
import os
import time
#import serial
import spidev
#import serial.tools.list_ports
import matplotlib
matplotlib.use('wxAgg')
import matplotlib.dates as md
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import pandas as pd
import numpy as np
from wx.lib import masked
from wx.lib.masked import NumCtrl
import wx.lib.agw.floatspin as FS
import random
import sys
import pprint
import pylab
import RPi.GPIO as GPIO
import mmis.Functions
from datetime import datetime


class Settings(wx.Panel):
    
    def __init__(self, parent, Module, pubsub1, pubsub2):

        wx.Panel.__init__(self, parent = parent)
        
        #self.spi = spidev.SpiDev()
        #self.spi.open(0,0)
        #self.spi.max_speed_hz = 50000

        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        self.calibrated_B = []
        self.paused = True
        self.pubsubname = pubsub1
        self.pubsubalarm = pubsub2

        #""" Creating a Timer """
         
        #self.redraw_timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 

        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        self.lblname1 = wx.StaticText(self, label = "Ambient Control :", pos = (40,30))
        self.lblname1.SetFont(self.font2)
        
        self.lblname2 = wx.StaticText(self, label = "Kp :", pos = (220,30))
        self.lblname2.SetFont(self.font2)
        #self.SET_Kp_Amb = NumCtrl(self, id = -1, value = 8.00,integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (250,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Kp_Amb = wx.SpinCtrlDouble(self, size=(150,-1), min =-400, max = 800, inc = 0.1, value='8.00', pos = (250,25))
        self.SET_Kp_Amb.SetDigits(5)
        self.SET_Kp_Amb.SetBackgroundColour('white')
        ################
        self.Kp_Data_Amb = 0
        self.Ki_Data_Amb = 0
        self.Kp_Data_N2 = 0
        self.Ki_Data_N2 = 0
        ################

        self.lblname3 = wx.StaticText(self, label = "Ki :", pos = (430,30))
        self.lblname3.SetFont(self.font2)
        #self.SET_Ki_Amb = NumCtrl(self, id = -1, value = 0.0099,integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (460,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Ki_Amb = wx.SpinCtrlDouble(self, size=(150,-1), min = 0, max = 800, inc = 0.1, value='8.00', pos = (460,25))
        self.SET_Ki_Amb.SetDigits(5)
        self.SET_Ki_Amb.SetBackgroundColour('white')

        self.button1 = wx.Button(self, label="Set", pos=(650, 25), size = (100,40), id = -1)
        self.button1.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TAMB_Params, self.button1)
        self.button1.SetForegroundColour('black')
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname4 = wx.StaticText(self, label = "Nitrogen Control :", pos = (40,85))
        self.lblname4.SetFont(self.font2)

        self.lblname5 = wx.StaticText(self, label = "Kp :", pos = (220,85))
        self.lblname5.SetFont(self.font2)
        #self.SET_Kp_N2 = NumCtrl(self, id = -1, value = 16.00, integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (250,80), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Kp_N2 = wx.SpinCtrlDouble(self, size=(150,-1), min =-400, max = 800, inc = 0.1, value='8.00', pos = (250,80))
        self.SET_Kp_N2.SetDigits(5)
        self.SET_Kp_N2.SetBackgroundColour('white')

        self.lblname6 = wx.StaticText(self, label = "Ki :", pos = (430,85))
        self.lblname6.SetFont(self.font2)
        #self.SET_Ki_N2 = NumCtrl(self, id = -1, value = 0.0099, integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(60,40), pos = (460,80), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Ki_N2 = wx.SpinCtrlDouble(self, size=(150,-1), min = 0, max = 800, inc = 0.1, value='8.00', pos = (460,80))
        self.SET_Ki_N2.SetDigits(5)
        self.SET_Ki_N2.SetBackgroundColour('white')

        self.button2 = wx.Button(self, label="Set", pos=(650, 80), size = (100,40), id = -1)
        self.button2.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TN2_Params,self.button2)
        self.button2.SetForegroundColour('black')
        self.button2.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname7 = wx.StaticText(self, label = "Module Information :", pos = (40,160))
        self.lblname7.SetFont(self.font2)
        self.Info = wx.TextCtrl(self, size=(200,100), pos = (220,130), style = wx.TE_LEFT|wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2)
        #self.Info.SetBackgroundColour('black')
        self.Info.SetFont(self.font2)

        self.button5 = wx.Button(self, label="Get Info", pos=(450, 160), size = (200,40), id = -1)
        self.button5.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_GET_INFO,self.button5)
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour(wx.Colour(211,211,211))

        self.button3 = wx.Button(self, label="Software Reset", pos=(40, 245), size = (200,40), id = -1)
        self.button3.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SOFT_RESET,self.button3)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour(wx.Colour(211,211,211))

        self.button4 = wx.Button(self, label="Alarm Reset", pos=(290, 245), size = (200,40), id = -1)
        self.button4.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_ALARM_RESET,self.button4)
        self.button4.SetForegroundColour('black')
        self.button4.SetBackgroundColour(wx.Colour(211,211,211))

        #self.lblname7 = wx.StaticText(self, label = "Mode :", pos = (40,85))
        #self.lblname7.SetFont(self.font2)
        #self.Mode_Selection = ['Digital', 'Analog']
        #self.Combo1 = wx.ComboBox(self, choices = self.Mode_Selection, pos = (200,80), size = (160,-1))
        
        #self.button2 = wx.Button(self, label="Set", pos=(380, 75), size = (100,40), id = -1)
        #self.button2.SetFont(self.font2)
        #self.Bind(wx.EVT_BUTTON, self.ON_SET_MODE,self.button2)
        #self.button2.SetForegroundColour('black')

        #self.lblname5 = wx.StaticText(self, label = "Module Name :", pos = (40,140))
        #self.lblname5.SetFont(self.font2)
        #self.Module_Name = wx.TextCtrl(self, size=(160,50), pos = (200,130), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)

        #self.lblname6 = wx.StaticText(self, label = "Version :", pos = (40,195))
        #self.lblname6.SetFont(self.font2)
        #self.Soft_Version = wx.TextCtrl(self, size=(160,40), pos = (200,185), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)

        #self.lblname6 = wx.StaticText(self, label = "Create Log File :", pos = (40,195))
        #self.lblname6.SetFont(self.font2)
        #self.File_name = wx.TextCtrl(self, size=(160,40), pos = (200,185), style = wx.TE_NO_VSCROLL|wx.TE_LEFT)
        
        #self.button4 = wx.Button(self, label="Get", pos=(380, 185), size = (100,40), id = -1)
        #self.button4.SetFont(self.font2)
        #self.Bind(wx.EVT_BUTTON, self.ON_VERSION_REQUEST,self.button4)
        #self.button4.SetForegroundColour('black')

        #self.button4 = wx.Button(self, label="Create", pos=(380, 185), size = (100,40), id = -1)
        #self.button4.SetFont(self.font2)
        #self.Bind(wx.EVT_BUTTON, self.ON_CREATE,self.button4)
        #self.button4.SetForegroundColour('black')
        self.Generate_startlogging_Event()
        self.SET_Kp_Amb.SetValue(str(self.Kp_Data_Amb))
        self.SET_Ki_Amb.SetValue(str(self.Ki_Data_Amb))
        self.SET_Kp_N2.SetValue(str(self.Kp_Data_N2))
        self.SET_Ki_N2.SetValue(str(self.Ki_Data_N2))

    def Generate_startlogging_Event(self):
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button5)
        evt.SetId(self.button5.GetId())
        self.button5.GetEventHandler().ProcessEvent(evt)

    def ON_GET_INFO(self, e):
        self.Info.Clear()
        name = mmis.Functions.GETTransactions(0X0C, self.chipselect, self.interruptpin)
        Version = mmis.Functions.GETTransactions(0X0D, self.chipselect, self.interruptpin)
        Kp_Amb = mmis.Functions.GETTransactions(0X12, self.chipselect, self.interruptpin)
        self.Kp_Data_Amb =  Kp_Amb.Float.Float[0]
        Ki_Amb = mmis.Functions.GETTransactions(0X13, self.chipselect, self.interruptpin)
        self.Ki_Data_Amb =  Ki_Amb.Float.Float[0]
        Kp_N2 = mmis.Functions.GETTransactions(0X16, self.chipselect, self.interruptpin)
        self.Kp_Data_N2 =  Kp_N2.Float.Float[0]
        Ki_N2 = mmis.Functions.GETTransactions(0X17, self.chipselect, self.interruptpin)
        self.Ki_Data_N2 =  Ki_N2.Float.Float[0]
        
        self.Info.SetDefaultStyle(wx.TextAttr(wx.BLUE))
        self.Info.AppendText(name.String + '- V' + Version.Version + '\n')
        self.Info.AppendText('Kp_Amb' + ' = ' + str(self.Kp_Data_Amb)[:8] + '\n')
        self.Info.AppendText('Ki_Amb' + ' = ' + str(self.Ki_Data_Amb)[:8] + '\n')
        self.Info.AppendText('Kp_N2' + ' = ' + str(self.Kp_Data_N2)[:8] + '\n')
        self.Info.AppendText('Ki_N2' + ' = ' + str(self.Ki_Data_N2)[:8])
        

    def ON_SET_TAMB_Params(self, e):
        Ki_Amb = str(self.SET_Ki_Amb.GetValue())
        Kp_Amb = str(self.SET_Kp_Amb.GetValue())
        set_Ki_Amb = mmis.Functions.SETTransactions(0X11, Ki_Amb , self.chipselect, self.interruptpin)
        time.sleep(0.5)
        set_Kp_Amb = mmis.Functions.SETTransactions(0X10, Kp_Amb , self.chipselect, self.interruptpin)

    def ON_SET_TN2_Params(self, e):
        Kp_N2 = str(self.SET_Kp_N2.GetValue())
        set_Kp_N2 = mmis.Functions.SETTransactions(0X14, Kp_N2 , self.chipselect, self.interruptpin)
        time.sleep(0.5)
        Ki_N2 = str(self.SET_Ki_N2.GetValue())
        set_Ki_N2 = mmis.Functions.SETTransactions(0X15, Ki_N2 , self.chipselect, self.interruptpin)

    def ON_MODULE_NAME(self, e):
        name = mmis.Functions.GETTransactions(0X0C, self.chipselect, self.interruptpin)
        print (name.Received)
        self.Module_Name.SetValue(name.String) 

    def ON_VERSION_REQUEST(self, e):
        Version = mmis.Functions.GETTransactions(0X0D, self.chipselect, self.interruptpin)
        print (Version.Version)
        self.Soft_Version.SetValue(Version.Version)

    def ON_SOFT_RESET(self, e):
        Reset = mmis.Functions.GETTransactions(0X0E, self.chipselect, self.interruptpin)
        print (Reset.Received)
        print (Reset.Character)
    
    def ON_ALARM_RESET(self, e):
        Reset = mmis.Functions.GETTransactions(0X0F, self.chipselect, self.interruptpin)
        print (Reset.Character)
    
    def OnCloseWindow(self, e):
        self.Destroy()

class Main(wx.Panel):

    def __init__(self, parent, Module, pubsub1, pubsub2):
        
        wx.Panel.__init__(self, parent = parent)

        """ SPI Communication port open"""
        #self.spi = spidev.SpiDev()
        #self.spi.open(0,0)
        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        pub.subscribe(self.OnBvalue, pubsub1)
        self.pubsub_logdata = pubsub2

        """ Initilize the lists to store the temperature data """
        self.data1 = []
        self.data2 = []
        self.paused_Amb = True   # At start up data generation event is paused until user starts it
        self.paused_N2 = True
        self.paused_Read = True
        self.A_PTC = 3.9083*math.pow(10,-3)
        self.B_PTC = -5.775*math.pow(10,-7)
        
        """ Creating a Timer for updating the Frame rate of the real time graph displayed"""
        self.redraw_graph_timer = wx.Timer(self)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer, self.redraw_graph_timer)  

        self.get_data_timer = wx.Timer(self)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer, self.get_data_timer)

        self.get_read_timer = wx.Timer(self)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_read_timer, self.get_read_timer)
        self.get_read_timer.Start(100)
        
        """ Initializing the graph plot to display the temperatures"""
        self.init_plot()
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.Xticks = 50

        """GRID and Font created"""
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font3 = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')


        """Create Buttons and other and Bind their events"""

        # Save Button - To save the graph in PNG format
        self.button3 = wx.Button(self, label = 'SaveGraph', size = (95,30), id=3)
        self.button3.SetFont(self.font3)
        self.button3.Bind(wx.EVT_BUTTON, self.OnSave)
        #self.button3.Bind(wx.EVT_BUTTON, self.on_pause_button_Read)     # this event changes the state of self.paused
        #self.button3.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button_Read) # this event updates buttons state between stop and start
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour('light green')

        # Stop/Start button - Data Acquisition
        self.button5 = wx.Button(self, label = 'Stop Amb', size = (100, 30), id =12)
        self.button5.SetFont(self.font2)
        self.button5.Bind(wx.EVT_BUTTON, self.on_pause_button_Amb)     # this event changes the state of self.paused
        self.button5.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button_Amb) # this event updates buttons state between stop and start
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('Red')

        # Stop/Start button - Data Acquisition
        self.button10 = wx.Button(self, label = 'Stop N2', size = (100, 30), id =67)
        self.button10.SetFont(self.font2)
        self.button10.Bind(wx.EVT_BUTTON, self.on_pause_button_N2)     # this event changes the state of self.paused
        self.button10.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button_N2) # this event updates buttons state between stop and start
        self.button10.SetForegroundColour('black')
        self.button10.SetBackgroundColour('Red')

        """# Check box - to show/delete x labels
        self.cb_xlab = wx.CheckBox(self, -1, 
            "Show X label",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)

        # Check box - to Show/delete the grid
        self.cb_grid = wx.CheckBox(self, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)"""

        # Static text and text control box - to display the current value of temperature
        self.lblname2 = wx.StaticText(self, label = "TA(C)")
        self.grid.Add(self.lblname2, pos = (0,0))
        self.lblname2.SetFont(self.font2)
        self.lblname2.SetForegroundColour('red')
        self.two = wx.TextCtrl(self, id = 40, size=(80,40), style = wx.TE_READONLY)
        self.two.SetBackgroundColour('grey')
        self.two.SetFont(self.font1)
        self.grid.Add(self.two, pos=(0,1))

        self.lblname5 = wx.StaticText(self, label = "TN2(C)")
        self.grid.Add(self.lblname5, pos = (2,0))
        self.lblname5.SetFont(self.font2)
        self.lblname5.SetForegroundColour('purple')
        self.five = wx.TextCtrl(self, id = 41, size=(80,40), style = wx.TE_READONLY)
        self.five.SetBackgroundColour('grey')
        self.five.SetFont(self.font1)
        self.grid.Add(self.five, pos=(2,1))

        self.lblname6 = wx.StaticText(self, label = "IA(mA)")
        self.grid.Add(self.lblname6, pos = (4,0))
        self.lblname6.SetFont(self.font2)
        self.lblname6.SetForegroundColour('red')
        self.six = wx.TextCtrl(self, id = 42, size=(80,40), style = wx.TE_READONLY)
        self.six.SetBackgroundColour('grey')
        self.six.SetFont(self.font1)
        self.grid.Add(self.six, pos=(4,1))

        self.lblname7 = wx.StaticText(self, label = "IN2(mA)")
        self.grid.Add(self.lblname7, pos = (3,0))
        self.lblname7.SetFont(self.font2)
        self.lblname7.SetForegroundColour('purple')
        self.seven = wx.TextCtrl(self, id = 43, size=(80,40), style = wx.TE_READONLY)
        self.seven.SetBackgroundColour('grey')
        self.seven.SetFont(self.font1)
        self.grid.Add(self.seven, pos=(3,1))

        self.lblname8 = wx.StaticText(self, label = "PA(mW)")
        self.grid.Add(self.lblname8, pos = (5,0))
        self.lblname8.SetFont(self.font2)
        self.lblname8.SetForegroundColour('red')
        self.eight = wx.TextCtrl(self, id = 44, size=(80,40), style = wx.TE_READONLY)
        self.eight.SetBackgroundColour('grey')
        self.eight.SetFont(self.font1)
        self.grid.Add(self.eight, pos=(5,1))

        self.lblname9 = wx.StaticText(self, label = "PN2(mW)")
        self.grid.Add(self.lblname9, pos = (6,0))
        self.lblname9.SetFont(self.font2)
        self.lblname9.SetForegroundColour('purple')
        self.nine = wx.TextCtrl(self, id = 45, size=(80,40), style = wx.TE_READONLY)
        self.nine.SetBackgroundColour('grey')
        self.nine.SetFont(self.font1)
        self.grid.Add(self.nine, pos=(6,1))
    

        # Static text and num control box -  to set the value of temperature
        self.button6 = wx.Button(self, label = 'Set-Tamb', size = (150,50), id=5)
        self.button6.SetFont(self.font2)
        self.button6.Bind(wx.EVT_BUTTON, self.SetAmbientTemperature)
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))
        #self.one = NumCtrl(self, id = 4,integerWidth=3, fractionWidth = 3, max = 800, autoSize = False, style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB, pos = (0,0))
        self.one = wx.SpinCtrlDouble(self, size=(150,-1), min =-400, max = 800, inc = 0.1, value='25')
        self.one.SetBackgroundColour('white')
        self.one.SetDigits(3)
        #self.one.SetFont(self.font1)

        # Static text and num control box -  to set the value of temperature
        self.button9 = wx.Button(self, label = 'Set-TN2', size = (150,50), id=13)
        self.button9.SetFont(self.font2)
        self.button9.Bind(wx.EVT_BUTTON, self.SetNitrogenTemperature)
        self.button9.SetBackgroundColour(wx.Colour(211,211,211))
        #self.four = NumCtrl(self, id = 14,integerWidth=3, fractionWidth = 3, max = 800, min = -400, autoSize = False, style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB, allowNegative = True)
        #self.four = wx.TextCtrl(self, id = 14, value = '0.000', size=(80,40), style = wx.TE_PROCESS_ENTER)
        #self.four.SetMaxLength = 8
        #self.four.Bind(wx.EVT_TEXT_MAXLEN, self.MaxLengthReached)
        self.four = wx.SpinCtrlDouble(self, size=(150,-1), min =-400, max = 800, inc = 0.1, value='180.001')
        self.four.SetDigits(3)
            
        self.four.SetBackgroundColour('white')
        #self.four.SetFont(self.font1)

        """# Static text and text control box - set the value to display the number of values on X -axis
        self.lblname3 = wx.StaticText(self, label = "X-Axis Length")
        self.grid.Add(self.lblname3, pos = (1,0))
        self.three = wx.TextCtrl(self, id = 6, size = (120,40), style = wx.TE_PROCESS_ENTER)
        self.three.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength)
        self.three.SetBackgroundColour('white')
        self.three.SetFont(self.font1)
        self.grid.Add(self.three, pos=(1,1))"""

        # create a normal bitmap button
        #bmp1 = wx.Bitmap("TEMPARATURE.png", wx.BITMAP_TYPE_ANY)
        #self.bmapBtn1 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp1, size=(74,70))

        # Set all the buttons, check boxes and text controls in a BOX
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(4)
        self.hbox1.Add(self.button3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(4)
        self.hbox1.Add(self.button10, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox2.Add(self.button1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox2.AddSpacer(5)
        self.hbox2.Add(self.button6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.AddSpacer(6)
        #self.hbox2.Add(self.button7, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox2.AddSpacer(5)
        self.hbox2.Add(self.button9, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox3.Add(self.button2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox3.AddSpacer(5)
        self.hbox3.Add(self.one, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.AddSpacer(6)
        #self.hbox3.Add(self.button8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox3.AddSpacer(5)
        self.hbox3.Add(self.four, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.lblname2, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(16)
        self.hbox4.Add(self.two, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(5)
        self.hbox4.Add(self.lblname5, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(10)
        self.hbox4.Add(self.five, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.lblname6, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.AddSpacer(8)
        self.hbox5.Add(self.six, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox5.AddSpacer(5)
        self.hbox5.Add(self.lblname7, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.AddSpacer(7)
        self.hbox5.Add(self.seven, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.lblname8, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox6.AddSpacer(3)
        self.hbox6.Add(self.eight, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox6.AddSpacer(5)
        self.hbox6.Add(self.lblname9, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox6.AddSpacer(3)
        self.hbox6.Add(self.nine, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        """self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.AddSpacer(20)
        self.hbox5.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.lblname3, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.AddSpacer(20)
        self.hbox6.Add(self.three, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        """
        self.vbox = wx.BoxSizer(wx.VERTICAL)      
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox6, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas, 3, flag=wx.LEFT | wx.TOP , border = 5)
        self.hbox.Add(self.vbox, 1.8, flag=wx.LEFT | wx.TOP )  
        
        self.SetSizer(self.hbox)
        self.hbox.Fit(self)
        self.GetAmbientTemperatureSetValue()
        self.GetN2TemperatureSetValue()

    def OnBvalue(self, value1, value2):
        self.A = value1
        self.B = value2
        self.Refresh()
    
    def Temperature_Acquisition(self):
        Temp = np.zeros(6)
        ADC_Amb = mmis.Functions.GETTransactions(0X19, self.chipselect, self.interruptpin)
        Voltage_Amb = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        Current_Amb = mmis.Functions.GETTransactions(0X08, self.chipselect, self.interruptpin)
        self.Alarm = ADC_Amb.Alarm
        try:
            ADC_Data_Amb =  ADC_Amb.Float.Float[0]
            Voltage_Data_Amb =  5.0 - 2*Voltage_Amb.Float.Float[0]*3.300/1024.0
            Current_Data_Amb =  Current_Amb.Float.Float[0]*3300.0/1024.0
        except AttributeError:
            ADC_Data_Amb = 0
            Voltage_Data_Amb = 0
            Current_Data_Amb = 0
        try:
            Resistance_Amb = ((ADC_Data_Amb-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_Amb))*10000
        except ZeroDivisionError:
            Resistance_Amb = 0
        
        ADC_N2 = mmis.Functions.GETTransactions(0X18, self.chipselect, self.interruptpin)
        Voltage_N2 = mmis.Functions.GETTransactions(0X09, self.chipselect, self.interruptpin)
        Current_N2 = mmis.Functions.GETTransactions(0X0A, self.chipselect, self.interruptpin)
        try:
            ADC_Data_N2 =  ADC_N2.Float.Float[0]
            Voltage_Data_N2 =  5.0 - 2*Voltage_N2.Float.Float[0]*3.300/1024.0
            Current_Data_N2 =  Current_N2.Float.Float[0]*3300.0/1024.0
        except AttributeError:
            ADC_Data_N2 = 0
            Voltage_Data_N2 = 0
            Current_Data_N2 = 0    
        try:
            Resistance_N2 = ((ADC_Data_N2-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_N2))*1000
        except ZeroDivisionError:
            Resistance_N2 = 0
     
        if Voltage_Data_Amb < 0:
            Voltage_Data_Amb = 0
        if Voltage_Data_N2 < 0:
            Voltage_Data_N2 = 0
        try:
            Temperature_Amb = 3435.0/(math.log(Resistance_Amb/0.09919119)) - 273.0
        except ValueError:
            #print ("Could not convert the data to integer")
            Temperature_Amb = -9999.0
        try:    
            Temperature_N2 = (-self.A_PTC+math.sqrt(self.A_PTC*self.A_PTC - 4*self.B_PTC*(1-(Resistance_N2/1000.0))))/(2*self.B_PTC)
            if (Temperature_N2 > 1000) or (Temperature_N2 < -300):
                Temperature_N2 = -9999.0
        except ValueError:
            #print ("Could not convert the data to integer")
            Temperature_N2 = -9999.0
            
        Temp[0] = Temperature_Amb
        Temp[1] = Voltage_Data_Amb
        Temp[2] = Current_Data_Amb
        Temp[3] = Temperature_N2
        Temp[4] = Voltage_Data_N2
        Temp[5] = Current_Data_N2
        pub.sendMessage(self.pubsub_logdata, data = Temp, alarm = self.Alarm)
        return Temp

    def init_plot(self):

        self.dpi = 60
        self.fig = Figure((5.0, 5.1), dpi = self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Temperature Control', size = 15)
        self.axes.set_xlabel('Samples(past 2 mins)', size = 15)
        self.axes.set_ylabel('Ambient Temperature (C)', color = 'red', size=12)

        #self.ax2 = self.fig.add_subplot(111, sharex = self.axes)
        self.ax2 = self.axes.twinx()
        #self.ax2.set_axis_bgcolor('black')
        #self.ax2.yaxis.tick_right()
        #self.ax2.yaxis.set_label_position("right")
        self.ax2.set_ylabel('Nitrogen Temperature (c)', color = 'purple', size=12)

        pylab.setp(self.axes.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes.get_yticklabels(), fontsize=12, color = 'red')

        pylab.setp(self.ax2.get_xticklabels(), fontsize=12)
        pylab.setp(self.ax2.get_yticklabels(), fontsize=12, color = 'purple')
        
        self.plot_data1 = self.axes.plot(
            self.data1,
            linewidth=1.5,
            color='red',
            )[0]

        self.plot_data2 = self.ax2.plot(
            self.data2,
            linewidth=1.5,
            color=(1,0,1),
            )[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.

        xmax = len(self.data1) if len(self.data1) > 400 else 400           
        xmin = 0
        #xmin = xmax - self.Xticks

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        ymin1 = round(min(self.data1[(-self.Xticks):]), 0) - 1
        ymax1 = round(max(self.data1[(-self.Xticks):]), 0) + 1

        ymin2 = round(min(self.data2[(-self.Xticks):]), 0) - 1
        ymax2 = round(max(self.data2[(-self.Xticks):]), 0) + 1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin1, upper=ymax1)
        self.ax2.set_xbound(lower=xmin, upper=xmax)
        self.ax2.set_ybound(lower=ymin2, upper=ymax2)
        self.axes.grid(True, color='gray')

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #
        """if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)"""
        
        pylab.setp(self.axes.get_xticklabels(), 
            visible=False)

        self.plot_data2.set_xdata(np.arange(len(self.data2)))
        self.plot_data2.set_ydata(np.array(self.data2))
        
        self.plot_data1.set_xdata(np.arange(len(self.data1)))
        self.plot_data1.set_ydata(np.array(self.data1))
        
        self.canvas.draw()
        
    def OnSetXLabelLength(self, e):
        Xtks = self.three.GetValue()
        self.Xticks = int(Xtks.encode())

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_pause_button_Amb(self, e):
        self.paused_Amb = not self.paused_Amb
        
        if self.paused_Amb:
            mmis.Functions.GETTransactions(0X03, self.chipselect, self.interruptpin)
        else:
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(250)

    def on_pause_button_N2(self, e):
        self.paused_N2 = not self.paused_N2
        
        if self.paused_N2:
            mmis.Functions.GETTransactions(0X04, self.chipselect, self.interruptpin)
        else:
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(250)
            
    def on_update_pause_button_Amb(self, e):
        if self.paused_Amb:
            label = "Start Amb"
            color = "light green"
            
        else:
            label = "Stop Amb"
            color = "red"
    
        self.button5.SetLabel(label)
        self.button5.SetBackgroundColour(color)

    def on_update_pause_button_N2(self, e):
        if self.paused_N2:
            label = "Start N2"
            color = "light green"
            #self.redraw_graph_timer.Stop()
            #self.get_data_timer.Stop()
            
        else:
            label = "Stop N2"
            color = "red"
    
        self.button10.SetLabel(label)
        self.button10.SetBackgroundColour(color)

    def on_redraw_graph_timer(self, e):
        self.draw_plot()

    def on_get_data_timer(self, e):
        if not self.paused_Amb or not self.paused_N2:
            if len(self.data1)<400:
                self.data1.append(self.x[0])
                self.data2.append(self.x[3])
            else:
                del self.data1[0]
                del self.data2[0]
                self.data1.append(self.x[0])
                self.data2.append(self.x[3])
        else:
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()

    def on_get_read_timer(self, e):
        #if not self.paused_Read:
        self.x = self.Temperature_Acquisition()
        self.two.SetValue(str(self.x[0])[:5])  # Temperature Ambient
        self.five.SetValue(str(self.x[3])[:5]) # Temperature Nitrogen
        self.six.SetValue(str(round(self.x[2], 0))) # Current Ambient
        self.seven.SetValue(str(round(self.x[5], 0))) # Current Nitrogen
        self.eight.SetValue(str(round(self.x[2] * self.x[1], 0)))
        self.nine.SetValue(str(round(self.x[5] * self.x[4], 0)))
        

    def SetAmbientTemperature(self, e):
        temp = self.one.GetValue()+273.0
        Rset = 10000*math.exp(-3435*((1/298.15)-(1/temp)))
        ADC = str(round(math.pow(2,15)*(1.5 - (Rset/(10000+Rset))),0))
        #ADC = str((1024*Rset)/(Rset+10000))
        #print (ADC)
        set_Tamb = mmis.Functions.SETTransactions(0X05, ADC , self.chipselect, self.interruptpin)
        self.GetAmbientTemperatureSetValue()

    def SetNitrogenTemperature(self, e):
        temp = self.four.GetValue()
        #print ("error found")
        Rset = 1000*(1+self.A_PTC*temp+self.B_PTC*temp*temp)
        ADC = str(round(math.pow(2,15)*(1.5 - (Rset/(1000+Rset))),0))
        #ADC = str((1024*Rset)/(Rset+1000))
        #print (ADC)
        set_Tn2 = mmis.Functions.SETTransactions(0X06, ADC , self.chipselect, self.interruptpin)
        self.GetN2TemperatureSetValue()
        
    def GetAmbientTemperatureSetValue(self):
        ADC_Amb = mmis.Functions.GETTransactions(0X1A, self.chipselect, self.interruptpin)
        ADC_Data_Amb =  ADC_Amb.Float.Float[0]
        Resistance_Amb = ((ADC_Data_Amb-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_Amb))*10000
        #Temperature_Amb = 3435.0/(math.log(Resistance_Amb/0.09919119)) - 273.0
        try:
            Temperature_Amb = 3435.0/(math.log(Resistance_Amb/0.09919119)) - 273.0
        except ValueError:
            #print ("Could not convert the data to integer")
            Temperature_Amb = -999.0
        self.button6.SetLabel("Set-Tamb\n"+str(round(Temperature_Amb,2)).center(10))
        self.button6.SetFont(self.font3)
        self.one.SetValue(round(Temperature_Amb,3))

    def GetN2TemperatureSetValue(self):
        ADC_N2 = mmis.Functions.GETTransactions(0X1B, self.chipselect, self.interruptpin)
        ADC_Data_N2 =  ADC_N2.Float.Float[0]
        Resistance_N2 = ((ADC_Data_N2-3*math.pow(2,14))/(math.pow(2,14)-ADC_Data_N2))*1000
        Temperature_N2 = (-self.A_PTC+math.sqrt(self.A_PTC*self.A_PTC - 4*self.B_PTC*(1-(Resistance_N2/1000.0))))/(2*self.B_PTC)
        self.button9.SetLabel("Set-TN2\n"+str(round(Temperature_N2,2)).center(10))
        self.button9.SetFont(self.font3)
        self.four.SetValue(str(round(Temperature_N2,4))[:8])

    def OnSave(self,e):
        file_choices = "PNG (*.png)|*.png"
        dlg = wx.FileDialog(
            self,
            message = "Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.FD_SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi = 200)

    def OnClose(self):
        self.Destroy()
