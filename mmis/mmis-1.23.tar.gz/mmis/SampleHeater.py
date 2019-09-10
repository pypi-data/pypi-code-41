import wx
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
from wx.lib.masked import NumCtrl
import pylab
import math
import RPi.GPIO as GPIO
import mmis.Functions
import mmis.DebugFunctions
from datetime import datetime

class Settings(wx.Panel):
    
    def __init__(self, parent, Module, pubsub1, pubsub2):

        wx.Panel.__init__(self, parent = parent)
        
        #self.spi = spidev.SpiDev()
        #self.spi.open(0,0)
        #self.spi.max_speed_hz = 50000

        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        self.B = []
        self.paused = True
        self.pubsubname = pubsub1
        self.pubsubalarm = pubsub2

        """ Creating a Timer """
         
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 

        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        
        self.lblname1 = wx.StaticText(self, label = "A :", pos = (40,30))
        self.lblname1.SetFont(self.font2)
        #self.SET_A = NumCtrl(self, id = -1, value = 0.25,integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (70,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_A = wx.SpinCtrlDouble(self, size=(150,40), min =0, max = 800, inc = 0.1, value='0.25', pos = (70,25))
        self.SET_A.SetDigits(3)
        self.SET_A.SetBackgroundColour('white')

        self.lblname7 = wx.StaticText(self, label = "B :", pos = (230,30))
        self.lblname7.SetFont(self.font2)
        self.SET_B = wx.TextCtrl(self, size=(150,40), pos = (260,25), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
        self.SET_B.SetBackgroundColour('grey')

        self.lblname2 = wx.StaticText(self, label = "T-Amb(C):", pos = (420,30))
        self.lblname2.SetFont(self.font2)
        #self.SET_Tamb = NumCtrl(self, id = -1, value = 20.0, integerWidth=6, fractionWidth = 3, min=-300, max = 800, size=(60,40), pos = (500,25), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Tamb = wx.SpinCtrlDouble(self, size=(150,40), min =-300, max = 800, inc = 0.1, value='20.00', pos = (500,25))
        self.SET_Tamb.SetDigits(3)
        self.SET_Tamb.SetBackgroundColour('white')
        
        self.button1 = wx.Button(self, label="Start Calibration", pos=(650, 25), size = (140,40), id = -1)
        self.button1.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_CALIBRATE_B, self.button1)
        self.button1.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button)
        self.button1.SetForegroundColour('black')

        self.lblname3 = wx.StaticText(self, label = "T-Max(C):", pos = (40,140))
        self.lblname3.SetFont(self.font2)
        #self.SET_Tmax = NumCtrl(self, id = -1, value = 800.0, integerWidth=6, fractionWidth = 3, min=0, max = 800, size=(80,40), pos = (200,130), limited = True, selectOnEntry = False, decimalChar = '.', groupChar = ',', groupDigits = True, name = "masked.number", useParensForNegatives = False)
        self.SET_Tmax = wx.SpinCtrlDouble(self, size=(160,40), min = 0, max = 800, inc = 0.1, value='800.00', pos = (200,130))
        self.SET_Tmax.SetDigits(3)
        self.SET_Tmax.SetBackgroundColour('white')

        self.button3 = wx.Button(self, label="Set", pos=(380, 130), size = (100,40), id = -1)
        self.button3.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_TMAX,self.button3)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname5 = wx.StaticText(self, label = "Resistance (Ohm):", pos = (40,195))
        self.lblname5.SetFont(self.font2)
        self.resistance = wx.TextCtrl(self, size=(150,40), pos = (200,185), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
        self.resistance.SetBackgroundColour('grey')

        myserial = self.getserial()
        if myserial=='00000000c5f39e78':
            self.lblname4 = wx.StaticText(self, label = "Calibration :", pos = (40,85))
            self.lblname4.SetFont(self.font2)
            self.Mode_Selection = ['Open Circuit', 'Short Circuit', '200 Ohm', 'CAL_MDAC']
            self.Combo1 = wx.ComboBox(self, choices = self.Mode_Selection, pos = (200,80), size = (160,-1))
            
            self.button2 = wx.Button(self, label="Set", pos=(380, 75), size = (100,40), id = -1)
            self.button2.SetFont(self.font2)
            self.Bind(wx.EVT_BUTTON, self.ON_SET_MODE,self.button2)
            self.button2.SetForegroundColour('black')
            self.button2.SetBackgroundColour(wx.Colour(211,211,211))

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
        
        #print (myserial)
        self.button5 = wx.Button(self, label="Software Reset", pos=(40, 245), size = (200,40), id = -1)
        self.button5.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SOFT_RESET,self.button5)
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour(wx.Colour(211,211,211))

        self.button6 = wx.Button(self, label="Alarm Reset", pos=(290, 245), size = (200,40), id = -1)
        self.button6.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_ALARM_RESET,self.button6)
        self.button6.SetForegroundColour('black')
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))

    def getserial(self):
      # Extract serial from cpuinfo file
      cpuserial = "0000000000000000"
      try:
        f = open('/proc/cpuinfo','r')
        for line in f:
          if line[0:6]=='Serial':
            cpuserial = line[10:26]
        f.close()
      except:
        cpuserial = "ERROR000000000"
     
      return cpuserial

    def ON_CALIBRATE_B(self, e):
        self.B.clear()
        self.paused = not self.paused
        self.A = self.SET_A.GetValue()
        self.Tamb = self.SET_Tamb.GetValue()
        print (self.A, self.Tamb)
        self.redraw_timer.Start(1000)

    def on_update_pause_button(self, e):
        if self.paused:
            label = "Start Calibration"
            color = "light green"
            self.redraw_timer.Stop()
        else:
            label = "Stop Calibration"
            color = "red"
    
        self.button1.SetLabel(label)
        self.button1.SetBackgroundColour(color)

    def on_redraw_timer(self, e):
        R = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        self.Alarm = R.Alarm
        pub.sendMessage(self.pubsubalarm, alarm = int(self.Alarm))
        Get_R = R.Float.Float[0]
        self.B.append((Get_R - (self.A*self.Tamb)))
        pub.sendMessage(self.pubsubname, value1 = self.A, value2 = self.B[len(self.B)-1]) # used Pubsub functionality to set data across different frames
        self.SET_B.SetValue(str(self.B[len(self.B)-1]))
        self.resistance.SetValue(str(Get_R))
        self.Stop_Calibration()
        

    def Stop_Calibration(self):
        if len(self.B)>4:
            delta_B = self.B[len(self.B)-1] - self.B[len(self.B)-5]
            if abs(delta_B)<0.1:
                print ("Calibration finished")
                self.paused = not self.paused
                self.button1.SetLabel("Start Calibration")
                self.button1.SetBackgroundColour("light green")
                self.redraw_timer.Stop()
            else:
                print ("Calibration still Going on ....")

        
    def ON_SET_TMAX(self, e):
        Tmax = self.SET_Tmax.GetValue()
        Rmax = str(self.A*Tmax + self.B[len(self.B)-1])
        set_tmax = mmis.Functions.SETTransactions(0X08, Rmax , self.chipselect, self.interruptpin)
        print (Rmax)
        
    def ON_SET_MODE(self, e):
        data = str(self.Combo1.GetSelection())
        if int(data) == 0:
            print ("Open Circuit Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X4E, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 1:
            print ("Short Circuit Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X4D, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 2:
            print ("200 Ohm Calibration Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X4C, self.chipselect, self.interruptpin, 4)
            print (mode.Received)
        elif int(data) == 3:
            print ("Calibration MDAC Going on")
            mode = mmis.DebugFunctions.GETTransactions(0X46, self.chipselect, self.interruptpin, 30)
            print (mode.Received)

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

        
        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        pub.subscribe(self.OnBvalue, pubsub1)
        self.pubsub_logdata = pubsub2
        
        """ Initilize the lists to store the temperature data """
        self.data = []
        self.paused = True   # At start up data generation event is paused until user starts it
        self.paused_P = True   # At start up data generation event is paused until user starts it
        self.paused_S = True   # At start up data generation event is paused until user starts it
        self.paused_R = True   # At start up data generation event is paused until user starts it
        self.BvalueSet = False
        self.set_power = 1.0  # initialize
        self.Integrator = 0 # initialize
        
        """ Creating a Timer for updating the Frame rate of the real time graph displayed"""
        self.redraw_graph_timer = wx.Timer(self, id = 2000)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer, self.redraw_graph_timer)  

        self.get_data_timer = wx.Timer(self, id = 2001)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer, self.get_data_timer)

        self.get_read_timer = wx.Timer(self, id = 2002)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_read_timer, self.get_read_timer)
        self.get_read_timer.Start(200)

        self.get_PID_timer = wx.Timer(self, id = 2003)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.PID, self.get_PID_timer)

        self.get_slope_timer = wx.Timer(self, id = 2004)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.slope_control, self.get_slope_timer)

        self.get_ramp_timer = wx.Timer(self, id = 2005)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.ramp_control, self.get_ramp_timer)
        
        """ Initializing the graph plot to display the temperatures"""
        self.init_plot()
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.Xticks = 50

        """GRID and Font created"""
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font3 = wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        """Control Mode Selection Box"""
        self.lblname1 = wx.StaticText(self, label = "Control Mode:")
        self.lblname1.SetFont(self.font2)
        self.Mode_Selection = ['T-Control', 'P-Control', 'Profile-Control', 'Ramp-Control']
        self.Combo1 = wx.ComboBox(self, choices = self.Mode_Selection, size = (140,-1))
        self.Combo1.Bind(wx.EVT_COMBOBOX, self.ON_SET_MODE)

        """Loads the profile for the Profile control"""
        self.button3 = wx.Button(self, label = 'Load Profile', size = (120,35), id=3)
        self.button3.SetFont(self.font2)
        self.button3.Bind(wx.EVT_BUTTON, self.OnFileOpen)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour('white')

        """Starts the Profile Control"""
        self.button4 = wx.Button(self, label = 'Start Ctrl', size = (120, 35), id =24)
        self.button4.SetFont(self.font1)
        self.button4.Bind(wx.EVT_BUTTON, self.on_pause_button_S)    
        self.button4.SetForegroundColour('black')
        self.button4.SetBackgroundColour('light green')

        """Starts the Temperature Control"""
        self.button5 = wx.Button(self, label = 'Start-T Ctrl', size = (120, 35), id =12)
        self.button5.SetFont(self.font1)
        self.button5.Bind(wx.EVT_BUTTON, self.on_pause_button)  
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('light green')

        """Starts the Power Control"""
        self.button8 = wx.Button(self, label = 'Start-P Ctrl', size = (120, 35), id =14)
        self.button8.SetFont(self.font1)
        self.button8.Bind(wx.EVT_BUTTON, self.on_pause_button_P)    
        self.button8.SetForegroundColour('black')
        self.button8.SetBackgroundColour('light green')

        """Starts the Ramp Control"""
        self.button9 = wx.Button(self, label = 'Start Ctrl', size = (120, 30), id =34)
        self.button9.SetFont(self.font1)
        self.button9.Bind(wx.EVT_BUTTON, self.on_pause_button_R)    
        self.button9.SetForegroundColour('black')
        self.button9.SetBackgroundColour('light green')

        # Check box - to show/delete x labels
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
        self.cb_grid.SetValue(True)

        # Static text and text control box - to display the current value of temperature
        self.lblname2 = wx.StaticText(self, label = "Temperature(\u00b0C)")
        self.grid.Add(self.lblname2, pos = (0,0))
        self.lblname2.SetFont(self.font2)
        self.two = wx.TextCtrl(self, id = 5, size=(135,35), style = wx.TE_READONLY)
        self.two.SetBackgroundColour('grey')
        self.two.SetFont(self.font1)
        self.grid.Add(self.two, pos=(0,1))

        # Static text and text control box - to display the current value of resistance
        self.lblname4 = wx.StaticText(self, label = "Resistance(\u2126)")
        self.grid.Add(self.lblname4, pos = (2,0))
        self.lblname4.SetFont(self.font2)
        self.four = wx.TextCtrl(self, id = 7, size=(135,35), style = wx.TE_READONLY)
        self.four.SetBackgroundColour('grey')
        self.four.SetFont(self.font1)
        self.grid.Add(self.four, pos=(2,1))

        # Static text and text control box - to display the current value of resistance
        self.lblname5 = wx.StaticText(self, label = "Power(mW)")
        self.grid.Add(self.lblname5, pos = (4,0))
        self.lblname5.SetFont(self.font2)
        self.five = wx.TextCtrl(self, id = 7, size=(135,35), style = wx.TE_READONLY)
        self.five.SetBackgroundColour('grey')
        self.five.SetFont(self.font1)
        self.grid.Add(self.five, pos=(3,1))

        # Static text and num control box -  to set the value of temperature
        self.button6 = wx.Button(self, label = 'Set(\u00b0C)', size = (57,35), id=5)
        self.button6.SetFont(self.font3)
        self.button6.Bind(wx.EVT_BUTTON, self.SetResistance)
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))
        self.one = wx.SpinCtrlDouble(self, size=(80,35), min =-300, max = 800, inc = 0.1, value='80.00')
        self.one.SetDigits(3)
        self.one.SetBackgroundColour('white')

        self.button7 = wx.Button(self, label = 'Set(mW)', size = (65,35), id=7)
        self.button7.SetFont(self.font3)
        self.button7.Bind(wx.EVT_BUTTON, self.SetPower)
        self.button7.SetBackgroundColour(wx.Colour(211,211,211))
        self.six = wx.SpinCtrlDouble(self, size=(70,35), min =0, max = 50, inc = 0.1, value='1.0')
        self.six.SetDigits(3)
        self.six.SetBackgroundColour('white')

        self.button10 = wx.Button(self, label = 'Set(_/\u203e)', size = (60,30), id=8) # Set slope
        self.button10.SetFont(self.font3)
        self.button10.Bind(wx.EVT_BUTTON, self.SetRampRate)
        self.button10.SetBackgroundColour(wx.Colour(211,211,211))
        self.seven = wx.SpinCtrlDouble(self, size=(80,30), min =-100, max = 100, inc = 0.1, value='10.0')
        self.seven.SetDigits(3)
        self.seven.SetBackgroundColour('white')

        self.button11 = wx.Button(self, label = 'Set(\u00b0C)', size = (60,30), id=15) # Set set point temperature
        self.button11.SetFont(self.font3)
        self.button11.Bind(wx.EVT_BUTTON, self.SetFinalTemperature)
        self.button11.SetBackgroundColour(wx.Colour(211,211,211))
        self.eight = wx.SpinCtrlDouble(self, size=(80,30), min =-300, max = 800, inc = 0.1, value='80.00')
        self.eight.SetDigits(3)
        self.eight.SetBackgroundColour('white')

        # Static text and text control box - set the value to display the number of values on X -axis
        self.lblname3 = wx.StaticText(self, label = "X-Axis Length")
        self.grid.Add(self.lblname3, pos = (1,0))
        self.three = wx.TextCtrl(self, id = 6, size = (70,30), style = wx.TE_PROCESS_ENTER)
        self.three.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength)
        self.three.SetBackgroundColour('white')
        self.three.SetFont(self.font1)
        self.grid.Add(self.three, pos=(1,1))

        # Set all the buttons, check boxes and text controls in a BOX
        self.hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox0.Add(self.lblname1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox0.Add(self.Combo1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.button8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.one, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.six, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button7, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.eight, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.Add(self.button11, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2_1.Add(self.seven, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.button10, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2_1.Add(self.button9, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.lblname2, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.AddSpacer(5)
        self.hbox3.Add(self.two, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.lblname4, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(25)
        self.hbox4.Add(self.four, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.lblname5, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.AddSpacer(40)
        self.hbox5.Add(self.five, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        #self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox5.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox5.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6.Add(self.lblname3, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.three, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox0, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        #self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2_1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox6, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas, 3.0, flag=wx.LEFT | wx.TOP)  
        self.hbox.Add(self.vbox, 1.99, flag=wx.LEFT | wx.TOP)  
        
        self.SetSizer(self.hbox)
        self.hbox.Fit(self)
        self.hbox2.Hide(0)
        self.hbox2.Hide(1)
        self.hbox2.Hide(2)
        self.hbox2.Hide(3)
        self.hbox2.Hide(4)
        self.hbox2.Hide(5)
        self.hbox2.Hide(6)
        self.hbox2.Hide(7)
        self.hbox2.Hide(8)
        self.hbox2.Hide(9)
        self.hbox2_1.Hide(0)
        self.hbox2_1.Hide(1)
        self.hbox2_1.Hide(2)

    def OnFileOpen(self,e):
        """Open a file"""
        self.dirname = ''
        self.Times = []
        self.SetPoints = []
        self.Slopes = []
        self.Comments = []
        mylines = []
        words = []
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.file = open(os.path.join(self.dirname, self.filename), 'rt')
            for myline in self.file:
                mylines.append(myline.partition('#')[0])
            #print (mylines)    
            #x = self.file.readlines()
            self.file.close()
            
            for line in mylines:
                for element in line.split():
                    words.append(element)
                    
        for i in range(int(len(words)/2 - 1)):
    
            self.Times.append(words[(i+1)*2])
            self.SetPoints.append(words[(i+1)*2+1])
            #self.Comments.append(words[(i+1)*3+2])
            
        self.Times = [float(i) for i in self.Times]
        self.Times = [i * 60 * 4 for i in self.Times] # Conversion to seconds from minutes
        self.SetPoints = [float(i) for i in self.SetPoints]
        
        #self.Slopes = [(a*1.0)/b for a, b in zip(self.SetPoints, self.Times)]
        current_temp = self.x[0]
        init_time = 0
        for i in range(len(self.Times)):
            self.Slopes.append((self.SetPoints[i]-current_temp)/(self.Times[i]-init_time))
            current_temp = self.SetPoints[i]
            init_time = self.Times[i]
        
        #print (self.Times)
        #print (self.SetPoints)
        #print (self.Slopes)
        #print (self.Comments)
        dlg.Destroy()


    def ON_SET_MODE(self, e):
        
        data = str(self.Combo1.GetSelection())
        if int(data) == 0:
            self.hbox2.Show(0)
            self.hbox2.Show(1)
            self.hbox2.Show(2)
            self.hbox2.Hide(3)
            self.hbox2.Hide(4)
            self.hbox2.Hide(5)
            self.hbox2.Hide(6)
            self.hbox2.Hide(7)
            self.hbox2.Hide(8)
            self.hbox2.Hide(9)
            self.hbox2_1.Hide(0)
            self.hbox2_1.Hide(1)
            self.hbox2_1.Hide(2)
            self.hbox.Layout()
            
        elif int(data) == 1:
            self.hbox2.Hide(0)
            self.hbox2.Hide(1)
            self.hbox2.Hide(2)
            self.hbox2.Show(3)
            self.hbox2.Show(4)
            self.hbox2.Show(5)
            self.hbox2.Hide(6)
            self.hbox2.Hide(7)
            self.hbox2.Hide(8)
            self.hbox2.Hide(9)
            self.hbox2_1.Hide(0)
            self.hbox2_1.Hide(1)
            self.hbox2_1.Hide(2)
            self.hbox.Layout()
            
        elif int(data) == 2:
            self.hbox2.Hide(0)
            self.hbox2.Hide(1)
            self.hbox2.Hide(2)
            self.hbox2.Hide(3)
            self.hbox2.Hide(4)
            self.hbox2.Hide(5)
            self.hbox2.Show(6)
            self.hbox2.Show(7)
            self.hbox2.Hide(8)
            self.hbox2.Hide(9)
            self.hbox2_1.Hide(0)
            self.hbox2_1.Hide(1)
            self.hbox2_1.Hide(2)
            self.hbox.Layout()
            
        elif int(data) == 3:
            self.hbox2.Hide(0)
            self.hbox2.Hide(1)
            self.hbox2.Hide(2)
            self.hbox2.Hide(3)
            self.hbox2.Hide(4)
            self.hbox2.Hide(5)
            self.hbox2.Hide(6)
            self.hbox2.Hide(7)
            self.hbox2.Show(8)
            self.hbox2.Show(9)
            self.hbox2_1.Show(0)
            self.hbox2_1.Show(1)
            self.hbox2_1.Show(2)
            self.hbox.Layout()
        
    def OnBvalue(self, value1, value2):
        self.BvalueSet = True
        self.A = value1
        self.B = value2
        #print (self.A, self.B)
        self.Refresh()
    
    def Temperature_Acquisition(self):
        try:
            Temp = np.zeros(4)
            Resistance = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
            Resistance_Data =  Resistance.Float.Float[0]
            self.Alarm = Resistance.Alarm
            Temperature_Data = ((Resistance_Data-self.B)/self.A)
            Voltage = mmis.Functions.GETTransactions(0X05, self.chipselect, self.interruptpin)
            Voltage_Data =  (Voltage.Float.Float[0]*5000.0)/(3.0*math.pow(2,24)) #in Volts
            Current = mmis.Functions.GETTransactions(0X06, self.chipselect, self.interruptpin)
            Current_Data =  (Current.Float.Float[0]*5000.0)/(3000*math.pow(2,24)) #in mA
            Temp[0] = Temperature_Data
            Temp[1] = Voltage_Data
            Temp[2] = Current_Data
            Temp[3] = Resistance_Data
            self.measured_power = Voltage_Data*Current_Data
            pub.sendMessage(self.pubsub_logdata, data = Temp, alarm = self.Alarm)
            return Temp
        except AttributeError:
            #print ("hello")
            pass

    def init_plot(self):

        self.dpi = 60
        self.fig = Figure((5.0, 5.1), dpi = self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('black')
        self.axes.set_title('Temperature acquisition', size = 15)
        self.axes.set_xlabel('Samples', size = 12)
        self.axes.set_ylabel('Ambient Temperature (C)', size = 15)

        pylab.setp(self.axes.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes.get_yticklabels(), fontsize=12)
        
        self.plot_data = self.axes.plot(
            self.data,
            linewidth=1,
            color=(1,1,0),
            )[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.

        xmax = len(self.data) if len(self.data) > 50 else 50           
        xmin = xmax - self.Xticks

        """ for ymin and ymax, find the minimal and maximal values
        in the data set and add a mininal margin.
        
        note that it's easy to change this scheme to the 
        minimal/maximal value in the current display, and not
        the whole data set. """
        
        ymin = round(min(self.data[(-self.Xticks):]), 0) - 1
        ymax = round(max(self.data[(-self.Xticks):]), 0) + 1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)
        
        pylab.setp(self.axes.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())
        
        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))
        self.canvas.draw()
        
    def OnSetXLabelLength(self, e):
        Xtks = self.three.GetValue()
        self.Xticks = int(Xtks.encode())

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_pause_button(self, e):
        """This function is used to set the state of the temperature control. Sends ON and OFF commands to the sample heater module for the temp
           control """
        self.paused = not self.paused
        if not self.paused_P:
            self.Generate_stop_Pctrl_Event()
        if not self.paused_S:
            self.Generate_stop_Sctrl_Event()
        if not self.paused_R:
            self.Generate_stop_Rctrl_Event()
        
        if self.paused:
            label = "Start-T Ctrl"
            color = "light green"
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
        else:
            label = "Stop-T Ctrl"
            color = "red"
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(200)

        self.button5.SetLabel(label)
        self.button5.SetBackgroundColour(color)

    def on_pause_button_P(self, e):
        """This function is used to set the state of the temperature control. Sends ON and OFF commands to the sample heater module for the temp
           control """
        self.paused_P = not self.paused_P
        if not self.paused:
            self.Generate_stop_Tctrl_Event()
        if not self.paused_S:
            self.Generate_stop_Sctrl_Event()
        if not self.paused_R:
            self.Generate_stop_Rctrl_Event()
        if self.paused_P:
            label = "Start-P Ctrl"
            color = "light green"
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()
            self.get_PID_timer.Stop()
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
        else:
            label = "Stop-P Ctrl"
            color = "red"
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(200)
            self.last_time = time.time()
            self.get_PID_timer.Start(250)
            self.Integrator = 0
            #print (self.set_power)

        self.button8.SetLabel(label)
        self.button8.SetBackgroundColour(color)

    def on_pause_button_S(self, e):
        """This function is used to set the state of the temperature control. Sends ON and OFF commands to the sample heater module for the temp
           control """
        self.paused_S = not self.paused_S
        if not self.paused:
            self.Generate_stop_Tctrl_Event()
        if not self.paused_P:
            self.Generate_stop_Pctrl_Event()
        if not self.paused_R:
            self.Generate_stop_Rctrl_Event()

        if self.paused_S:
            label = "Start Ctrl"
            color = "light green"
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()
            self.get_slope_timer.Stop()
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
        else:
            label = "Stop Ctrl"
            color = "red"
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(200)
            self.get_slope_timer.Start(230)
            self.Count_Seconds = 0
            

        self.button4.SetLabel(label)
        self.button4.SetBackgroundColour(color)

    def on_pause_button_R(self, e):  
        """This function is used to set the state of the temperature Ramp control. Sends ON and OFF commands to the sample heater module for the temp
           control """
        self.paused_R = not self.paused_R
        
        if not self.paused:
            self.Generate_stop_Tctrl_Event()
        if not self.paused_P:
            self.Generate_stop_Pctrl_Event()
        if not self.paused_S:
            self.Generate_stop_Sctrl_Event()

        if self.paused_R:
            label = "Start Ctrl"
            color = "light green"
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()
            self.get_ramp_timer.Stop()
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)
        else:
            label = "Stop Ctrl"
            color = "red"
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(200)
            self.get_ramp_timer.Start(230)
            self.init_ramp_temp = self.x[0]

        self.button9.SetLabel(label)
        self.button9.SetBackgroundColour(color)


    def Generate_stop_Tctrl_Event(self):
        #print("T Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button5)
        evt.SetId(self.button5.GetId())
        self.button5.GetEventHandler().ProcessEvent(evt)

    def Generate_stop_Pctrl_Event(self):
        #print("P Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button8)
        evt.SetId(self.button8.GetId())
        self.button8.GetEventHandler().ProcessEvent(evt)

    def Generate_stop_Sctrl_Event(self):
        #print("S Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button4)
        evt.SetId(self.button4.GetId())
        self.button4.GetEventHandler().ProcessEvent(evt)

    def Generate_stop_Rctrl_Event(self):
        #print("R Control Event")
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId)
        evt.SetEventObject(self.button9)
        evt.SetId(self.button9.GetId())
        self.button9.GetEventHandler().ProcessEvent(evt)

    def on_redraw_graph_timer(self, e):
        """This interrupt is generated by the graph timer for updating the graph every 1 second."""
        self.draw_plot()

    def on_get_data_timer(self, e):
        """The interrupt is generated every 200ms when start control (data_timer) gets a start. Total data points to be stored in buffer
           is limited to 2100 and beyond that based FIFO the data gets cleared."""
        
        if not (self.paused and self.paused_P and self.paused_S and self.paused_R):
            if len(self.data)<2100:
                self.data.append(self.x[0])
            else:
                del self.data[0]
                self.data.append(self.x[0])

    def on_get_read_timer(self, e):
        """The interrupt is generated every few milliseconds by read_timer interrupt to update the values of Temperature and Resistance
           onto the control window of GUI. These values get updated only if the Bvalue is set atleast once"""
        if self.BvalueSet == True:
            self.x = self.Temperature_Acquisition()
            self.two.SetValue(str(self.x[0])[:6])
            self.four.SetValue(str(self.x[3])[:6])
            self.five.SetValue(str(self.measured_power)[:6])

    def SetResistance(self, e):
        """Temperature set point is retreived from the GUI and is converterd to Resistance with the function R=A*T+B
            and the new resistance set point is written to the sample heater module"""
        temp = self.one.GetValue()
        #print (temp)
        Rset = str(temp*self.A + self.B)
        set_rset = mmis.Functions.SETTransactions(0X03, Rset , self.chipselect, self.interruptpin)

    def SetPower(self, e):
        self.set_power = self.six.GetValue()
        self.Integrator = 0

    def SetRampRate(self, e):
        self.set_ramp = self.seven.GetValue()/4.0

    def SetFinalTemperature(self, e):
        self.final_temperature = self.eight.GetValue()

    def ramp_control(self, e):
        if (self.set_ramp > 0 and self.final_temperature > self.init_ramp_temp):
            self.init_ramp_temp = self.init_ramp_temp + self.set_ramp
            if (self.init_ramp_temp <= self.final_temperature):
                self.New_SetResistance(self.init_ramp_temp)
            else:
                self.New_SetResistance(self.final_temperature)
                self.init_ramp_temp = self.init_ramp_temp - self.set_ramp
        elif (self.set_ramp < 0 and self.final_temperature < self.init_ramp_temp):
            self.init_ramp_temp = self.init_ramp_temp + self.set_ramp
            if (self.init_ramp_temp >= self.final_temperature):
                self.New_SetResistance(self.init_ramp_temp)
            else:
                self.New_SetResistance(self.final_temperature)
                self.init_ramp_temp = self.init_ramp_temp + self.set_ramp
        
    def New_SetResistance(self, temp):
        """Temperature set point is retreived from the GUI and is converterd to Resistance with the function R=A*T+B
            and the new resistance set point is written to the sample heater module"""
    
        Rset = str(temp*self.A + self.B)
        set_rset = mmis.Functions.SETTransactions(0X03, Rset , self.chipselect, self.interruptpin)


    def PID(self, e):
        Kp = 7
        Ki = 3
        error = self.set_power - self.measured_power
        if error < 0: error = 0
        self.P_value = Kp*error
        self.Integrator = self.Integrator+error
        if self.Integrator > 1000: self.Integrator = 1000
        elif self.Integrator < -1000: self.Integrator = -1000
        self.I_value = self.Integrator*Ki
        PID = self.P_value+self.I_value
        #print (PID)
        if PID<20: PID=20.0
        self.New_SetResistance(PID)

    def slope_control(self, e):
        self.Count_Seconds = self.Count_Seconds+1
        if (self.Count_Seconds > 1):
            self.New_SetResistance(self.init_temp)
            if ((self.Count_Seconds-2) == self.Times[self.count_setpoint]):
                self.New_SetResistance(self.SetPoints[self.count_setpoint])
                self.init_temp = self.SetPoints[self.count_setpoint]
                self.count_setpoint = self.count_setpoint+1
                self.init_time = self.Count_Seconds
                if (self.count_setpoint == len(self.SetPoints)):
                    self.slope = 0
                    self.count_setpoint = self.count_setpoint - 1
                else:
                    self.slope = self.Slopes[self.count_setpoint]
                
            self.init_temp = self.init_temp+self.slope
            #print (self.init_temp)
            
        else:
            self.init_temp = self.x[0]
            self.init_time = 0
            self.count_setpoint = 0
            self.slope = self.Slopes[0]
            

    def OnSave(self,e):
        """This function allows to get the screenshot of the live graph runnning on GUI"""
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
        """Destroys all the events subjected to the Sample heater class"""
        self.Destroy()
