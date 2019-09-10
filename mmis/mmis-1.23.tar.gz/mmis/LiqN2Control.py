import wx
from wx.lib.pubsub import pub
import os
import time
import spidev
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
from datetime import datetime

#ImgFolder = '/home/pi/Desktop/package/mmis-test/Images/'
#ImgFolder = '/usr/local/lib/python3.5/dist-packages/mmis/Images/' 
ImgFolder = '/home/pi/.local/lib/python3.5/site-packages/mmis/Images/'
class Settings(wx.Panel):
    
    def __init__(self, parent, Module, pubsub1, pubsub2):

        wx.Panel.__init__(self, parent = parent)

        self.chipselect = Module[0]
        self.interruptpin = Module[1]

        self.paused = True
        self.pubsubname = pubsub1
        self.pubsubalarm = pubsub2

        """ Creating a Timer """
         
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 

        """ Creating buttons and labels """

        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        
        self.lblname1 = wx.StaticText(self, label = "Kp :", pos = (40,30))
        self.lblname1.SetFont(self.font2)
        self.SET_Kp = wx.SpinCtrlDouble(self, size=(100,40), min =0, max = 200.0, inc = 0.01, value='50.0', pos = (80,20))
        self.SET_Kp.SetDigits(3)
        self.SET_Kp.SetBackgroundColour('white')

        self.button0 = wx.Button(self, label="Set Kp", pos=(200, 20), size = (80,40), id = -1)
        self.button0.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_Kp,self.button0)
        self.button0.SetForegroundColour('black')
        self.button0.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname2 = wx.StaticText(self, label = "Anti-Rewound limit :", pos = (320,30))
        self.lblname2.SetFont(self.font2)
        self.SET_Rewound = wx.SpinCtrlDouble(self, size=(150,40), min = 0.5, max = 2.5, inc = 0.1, value='0.65', pos = (480,20))
        self.SET_Rewound.SetDigits(3)
        self.SET_Rewound.SetBackgroundColour('white')

        self.button1 = wx.Button(self, label="Set", pos=(660, 20), size = (100,40), id = -1)
        self.button1.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_Rewound,self.button1)
        self.button1.SetForegroundColour('black')
        self.button1.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname3 = wx.StaticText(self, label = "Capacitance pF:", pos = (40,85))
        self.lblname3.SetFont(self.font2)
        self.Capacitance = wx.TextCtrl(self, size=(150,30), pos = (200,80), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
        self.Capacitance.SetBackgroundColour('grey')
        
        self.button2 = wx.Button(self, label="Measure", pos=(380, 75), size = (140,40), id = -1)
        self.button2.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_Read_Capacitance, self.button2)
        self.button2.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button)
        self.button2.SetForegroundColour('black')
        
        self.lblname4 = wx.StaticText(self, label = "Slope :", pos = (40,190))
        self.lblname4.SetFont(self.font2)
        self.SET_Slope = wx.SpinCtrlDouble(self, size=(100,40), min = 0, max = 1000, inc = 0.01, value='0.001', pos = (105,180))
        self.SET_Slope.SetDigits(3)
        self.SET_Slope.SetBackgroundColour('white')

        self.lblname5 = wx.StaticText(self, label = "Upper-Limit :", pos = (215,190))
        self.lblname5.SetFont(self.font2)
        self.SET_UL = wx.SpinCtrlDouble(self, size=(100,40), min = 0, max = 3.0, inc = 0.01, value='1.1', pos = (325,180))
        self.SET_UL.SetDigits(3)
        self.SET_UL.SetBackgroundColour('white')
        
        self.lblname6 = wx.StaticText(self, label = "Lower-Limit :", pos = (435,190))
        self.lblname6.SetFont(self.font2)
        self.SET_LL = wx.SpinCtrlDouble(self, size=(100,40), min = 0, max = 3.0, inc = 0.01, value='0.65', pos = (545,180))
        self.SET_LL.SetDigits(3)
        self.SET_LL.SetBackgroundColour('white')

        self.button3 = wx.Button(self, label="Set", pos=(660, 180), size = (100,40), id = -1)
        self.button3.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SET_SLOPE,self.button3)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour(wx.Colour(211,211,211))

        self.lblname7 = wx.StaticText(self, label = "Motor Manual Control :", pos = (40,140))
        self.lblname7.SetFont(self.font2)
        self.button4 = wx.Button(self, label="Forward", pos=(260, 130), size = (100,40), id = -1)
        self.button4.SetFont(self.font2)
        self.button4.Bind(wx.EVT_LEFT_DOWN, self.ON_Forward)
        self.button4.Bind(wx.EVT_LEFT_UP, self.ON_Break)
        self.button4.SetForegroundColour('black')
        self.button4.SetBackgroundColour(wx.Colour(211,211,211))

        self.button5 = wx.Button(self, label="Reverse", pos=(380, 130), size = (100,40), id = -1)
        self.button5.SetFont(self.font2)
        self.button5.Bind(wx.EVT_LEFT_DOWN, self.ON_Backward)
        self.button5.Bind(wx.EVT_LEFT_UP, self.ON_Break)
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour(wx.Colour(211,211,211))
        
        self.button6 = wx.Button(self, label="Software Reset", pos=(40, 245), size = (200,40), id = -1)
        self.button6.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_SOFT_RESET,self.button6)
        self.button6.SetForegroundColour('black')
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))

        self.button7 = wx.Button(self, label="Alarm Reset", pos=(290, 245), size = (200,40), id = -1)
        self.button7.SetFont(self.font2)
        self.Bind(wx.EVT_BUTTON, self.ON_ALARM_RESET,self.button7)
        self.button7.SetForegroundColour('black')
        self.button7.SetBackgroundColour(wx.Colour(211,211,211))

        self.Logo = wx.StaticBitmap(self, -1, pos = (590,65))
        self.image_file = ImgFolder+'liquid-nitrogen.png'
        self.Logo.SetFocus()
        self.Logo.SetBitmap(wx.Bitmap(self.image_file))

        myserial = self.getserial()
        """debug mode works only on local RPi
        if myserial=='00000000e138f974':"""
        print (myserial)

    def ON_Forward(self, e):
        #print ("mouse entered")
        mmis.Functions.SETTransactions(0X0A, str(int(1)) , self.chipselect, self.interruptpin)

    def ON_Backward(self, e):
        #print ("mouse backward")
        mmis.Functions.SETTransactions(0X0B, str(int(2)) , self.chipselect, self.interruptpin)

    def ON_Break(self, e):
        #print ("mouse left")
        mmis.Functions.SETTransactions(0X10, str(int(0)) , self.chipselect, self.interruptpin)

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

    def ON_Read_Capacitance(self, e):
        self.paused = not self.paused
        self.redraw_timer.Start(1000)

    def on_update_pause_button(self, e):
        if self.paused:
            label = "Start Measuring"
            color = "light green"
            self.redraw_timer.Stop()
        else:
            label = "Stop Measuring"
            color = "red"
    
        self.button2.SetLabel(label)
        self.button2.SetBackgroundColour(color)

    def on_redraw_timer(self, e):
        c = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        self.Alarm = c.Alarm
        Cap = c.Float.Float[0]
        if (Cap > 3.0):
            self.Capacitance.SetValue("Out of Range")
        else:
            self.Capacitance.SetValue(str(Cap)[:6] + " pF")

    def ON_SET_Kp(self, e):
        Kp = str(self.SET_Kp.GetValue()) # Refill Capacitance buffer
        set_Kp = mmis.Functions.SETTransactions(0X11, Kp , self.chipselect, self.interruptpin)
        print (Kp)
        
    def ON_SET_Rewound(self, e):
        C_Rw = str(self.SET_Rewound.GetValue()) # Rewound Capacitance limit
        set_rewound = mmis.Functions.SETTransactions(0X12, C_Rw , self.chipselect, self.interruptpin)
        print (C_Rw)

    def ON_SET_SLOPE(self, e):
        C_UL = str(self.SET_UL.GetValue()) # Upper limit for slope control
        C_LL = str(self.SET_LL.GetValue()) # Lower limit for slope control
        Slope = str(self.SET_Slope.GetValue()) # Slope
        set_upperlimit = mmis.Functions.SETTransactions(0X16, C_UL , self.chipselect, self.interruptpin)
        set_lowerlimit = mmis.Functions.SETTransactions(0X17, C_LL , self.chipselect, self.interruptpin)
        set_slope = mmis.Functions.SETTransactions(0X15, Slope , self.chipselect, self.interruptpin)
        print (C_UL, C_LL, Slope)

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

        self.pubsub_logdata = pubsub2
        
        """ Initilize the lists to store the temperature data """
        self.data = []
        self.N2paused = True   # At start up data generation event is paused until user starts it
        self.Slope_paused = True
        
        """ Creating a Timer for updating the Frame rate of the real time graph displayed"""
        self.redraw_graph_timer = wx.Timer(self, id = 2000)      # this timer controls the frame rate of the graph display
        self.Bind(wx.EVT_TIMER, self.on_redraw_graph_timer, self.redraw_graph_timer)  

        self.get_data_timer = wx.Timer(self, id = 2001)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_data_timer, self.get_data_timer)

        self.get_read_timer = wx.Timer(self, id = 2002)          # this timer controls the sampling rate of the data
        self.Bind(wx.EVT_TIMER, self.on_get_read_timer, self.get_read_timer)
        self.get_read_timer.Start(200)
        
        
        """ Initializing the graph plot to display the temperatures"""
        self.init_plot()
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.Xticks = 50

        """GRID and Font created"""
        self.grid = wx.GridBagSizer(hgap=5, vgap=5)
        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font3 = wx.Font(10, wx.MODERN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD, False, u'Consolas')

        """Create Buttons and other and Bind their events"""

        self.lblname6 = wx.StaticText(self, label = "LiqN2 CTRL")
        self.lblname6.SetFont(self.font3)
        self.lblname6.SetForegroundColour('Blue')
        self.lblname7 = wx.StaticText(self, label = "Graph")
        self.lblname7.SetFont(self.font3)
        self.lblname7.SetForegroundColour('Blue')
        self.lblname8 = wx.StaticText(self, label = "Slope CTRL")
        self.lblname8.SetFont(self.font3)
        self.lblname8.SetForegroundColour('Blue')

        # Stop/Start button - Data Acquisition
        self.button5 = wx.Button(self, label = 'Stop Ctrl', size = (80, 35), id =12)
        self.button5.SetFont(self.font1)
        self.button5.Bind(wx.EVT_BUTTON, self.on_pause_start_button)     # this event changes the state of self.paused
        self.button5.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_start_button) # this event updates buttons state between stop and start
        self.button5.SetForegroundColour('black')
        self.button5.SetBackgroundColour('Red')

        # Stop/Start button - Data Acquisition
        self.button4 = wx.Button(self, label = 'Slope Ctrl', size = (80, 35), id =12)
        self.button4.SetFont(self.font1)
        self.button4.Bind(wx.EVT_BUTTON, self.on_pause_slope_button)     # this event changes the state of self.paused
        self.button4.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_slope_button) # this event updates buttons state between stop and start
        self.button4.SetForegroundColour('black')
        self.button4.SetBackgroundColour('Red')

        # Save Button - To save the graph in PNG format
        self.button3 = wx.Button(self, label = 'Snap', size = (80,35), id=3)
        self.button3.SetFont(self.font1)
        self.button3.Bind(wx.EVT_BUTTON, self.OnSave)
        self.button3.SetForegroundColour('black')
        self.button3.SetBackgroundColour('light green')
        
        # Static text and text control box - to display the current value of Capacitance
        self.lblname2 = wx.StaticText(self, label = "Capacitance")
        self.grid.Add(self.lblname2, pos = (0,0))
        self.lblname2.SetFont(self.font2)
        self.two = wx.TextCtrl(self, id = 5, size=(135,35), style = wx.TE_READONLY)
        self.two.SetBackgroundColour('grey')
        self.two.SetFont(self.font1)

        # Static text and text control box - to display the current value of resistance
        self.lblname4 = wx.StaticText(self, label = "Resistance")
        self.lblname4.SetFont(self.font2)
        self.four = wx.TextCtrl(self, id = 5, size=(135,35), style = wx.TE_READONLY)
        self.four.SetBackgroundColour('grey')
        self.four.SetFont(self.font1)

        # Static text and text control box - to display the current value of motor current
        self.lblname5 = wx.StaticText(self, label = "Current")
        self.lblname5.SetFont(self.font2)
        self.five = wx.TextCtrl(self, id = 5, size=(135,35), style = wx.TE_READONLY)
        self.five.SetBackgroundColour('grey')
        self.five.SetFont(self.font1)

        # Static text and num control box -  to set the value of temperature
        self.lblname1 = wx.StaticText(self, label = "Cap(pF) CTRL")
        self.lblname1.SetFont(self.font2)
        self.button6 = wx.Button(self, label = 'Set', size = (50,35), id=5)
        self.button6.SetFont(self.font2)
        self.button6.Bind(wx.EVT_BUTTON, self.SetCapacitance)
        self.button6.SetBackgroundColour(wx.Colour(211,211,211))
        self.one = wx.SpinCtrlDouble(self, size=(85,35), min = 0, max = 2, inc = 0.001, value='0.75')
        self.one.SetDigits(3)
        self.one.SetBackgroundColour('white')

        # Static text and text control box - set the value to display the number of values on X -axis
        self.lblname3 = wx.StaticText(self, label = "X-Axis Length")
        self.grid.Add(self.lblname3, pos = (1,0))
        self.three = wx.TextCtrl(self, id = 6, size = (80,35), style = wx.TE_PROCESS_ENTER)
        self.three.Bind(wx.EVT_TEXT_ENTER, self.OnSetXLabelLength)
        self.three.SetBackgroundColour('white')
        self.three.SetFont(self.font1)
        self.grid.Add(self.three, pos=(1,1))

        # Check box - to show/delete x labels
        self.cb_xlab = wx.CheckBox(self, -1, 
            "Show X label",
            style=wx.ALIGN_RIGHT)
        self.cb_xlab.SetFont(self.font2)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)

        # Check box - to Show/delete the grid
        self.cb_grid = wx.CheckBox(self, -1, 
            "Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        # Set all the buttons, check boxes and text controls in a BOX
        self.hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox0.Add(self.lblname6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox0.AddSpacer(12)
        self.hbox0.Add(self.lblname7, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox0.AddSpacer(20)
        self.hbox0.Add(self.lblname8, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.button5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(5)
        self.hbox1.Add(self.button3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(5)
        self.hbox1.Add(self.button4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.lblname1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.AddSpacer(7)
        self.hbox2.Add(self.one, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox2.Add(self.button1, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox2.AddSpacer(7)
        self.hbox2.Add(self.button6, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.lblname2, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox3.AddSpacer(20)
        self.hbox3.Add(self.two, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.lblname4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.AddSpacer(30)
        self.hbox4.Add(self.four, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5.Add(self.lblname5, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.AddSpacer(55)
        self.hbox5.Add(self.five, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.vbox1 = wx.BoxSizer(wx.VERTICAL)
        self.vbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.vbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox7.Add(self.lblname3, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox7.AddSpacer(10)
        self.hbox7.Add(self.three, border = 5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox7.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #self.hbox7.Add(self.vbox1,1, flag=wx.LEFT | wx.TOP)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox0, 0, flag=wx.ALIGN_LEFT | wx.TOP, border = 0)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP, border = 0)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP, border = 0)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_LEFT | wx.TOP, border = 0)
        self.vbox.Add(self.hbox4, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox5, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox7, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.canvas, 3.0, flag=wx.LEFT | wx.TOP)  
        self.hbox.Add(self.vbox, 1.99, flag=wx.LEFT | wx.TOP)  
        
        self.SetSizer(self.hbox)
        self.hbox.Fit(self)
    
    def Temperature_Acquisition(self):
        Temp = np.zeros(3)
        Capacitance = mmis.Functions.GETTransactions(0X07, self.chipselect, self.interruptpin)
        Capacitance_Data =  Capacitance.Float.Float[0]
        self.Alarm = Capacitance.Alarm
        Current = mmis.Functions.GETTransactions(0X09, self.chipselect, self.interruptpin)
        Current_Data = Current.Float.Float[0]
        #print (Current_Data)
        Current_Data = Current_Data*530.6*3.3/255.0
        Resistance_Data = 0
        Temp[0] = Capacitance_Data
        Temp[1] = Current_Data
        Temp[2] = Resistance_Data
        pub.sendMessage(self.pubsub_logdata, data = Temp, alarm = self.Alarm)
        return Temp

    def init_plot(self):

        self.dpi = 60
        self.fig = Figure((5.0, 5.1), dpi = self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('brown')
        self.axes.set_title('Capacitance acquisition', size = 15)
        self.axes.set_xlabel('Samples', size = 12)
        self.axes.set_ylabel('Capacitance (pF)', size = 15)

        pylab.setp(self.axes.get_xticklabels(), fontsize=12)
        pylab.setp(self.axes.get_yticklabels(), fontsize=12)
        
        self.plot_data = self.axes.plot(
            self.data,
            linewidth=2,
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

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        ymin = (min(self.data[(-self.Xticks):])) - 0.1
        ymax = (max(self.data[(-self.Xticks):])) + 0.1

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
        #self.plot_data.set_xdata(np.array(self.time))
        self.plot_data.set_ydata(np.array(self.data))
        #self.two.SetValue(str(self.x[0]))
        self.canvas.draw()
        
    def OnSetXLabelLength(self, e):
        Xtks = self.three.GetValue()
        self.Xticks = int(Xtks.encode())

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_pause_start_button(self, e):
        self.N2paused = not self.N2paused
        
        if self.N2paused:
            mmis.Functions.GETTransactions(0X03, self.chipselect, self.interruptpin)
        else:
            mmis.Functions.GETTransactions(0X01, self.chipselect, self.interruptpin)
            self.redraw_graph_timer.Start(1000)
            self.get_data_timer.Start(200)
            

    def on_update_pause_start_button(self, e):
        if self.N2paused:
            label = "Start"
            color = "light green"
            self.redraw_graph_timer.Stop()
            self.get_data_timer.Stop()
            
        else:
            label = "Stop"
            color = "red"
    
        self.button5.SetLabel(label)
        self.button5.SetBackgroundColour(color)

    def on_pause_slope_button(self, e):
        self.Slope_paused = not self.Slope_paused
        
        if self.Slope_paused:
            mmis.Functions.GETTransactions(0X04, self.chipselect, self.interruptpin)
        else:
            mmis.Functions.GETTransactions(0X02, self.chipselect, self.interruptpin)

    def on_update_pause_slope_button(self, e):
        if self.Slope_paused:
            label = "Start"
            color = "light green"
            
        else:
            label = "Stop"
            color = "red"
    
        self.button4.SetLabel(label)
        self.button4.SetBackgroundColour(color)

    def on_redraw_graph_timer(self, e):
        self.draw_plot()

    def on_get_data_timer(self, e):
        if not self.N2paused:
            if len(self.data)<2100:
                #self.x = self.Temperature_Acquisition()
                self.data.append(self.x[0])
            else:
                del self.data[0]
                #self.x = self.Temperature_Acquisition()
                self.data.append(self.x[0])

    def on_get_read_timer(self, e):
        self.x = self.Temperature_Acquisition()
        if (self.x[0] > 3.0):
            self.two.SetValue("Out of Range")
        else:
            self.two.SetValue(str(self.x[0])[:5] + " pF")
        self.five.SetValue(str(self.x[1])[:6] + " mA")
        #print (str(self.x[1])[:6])
        

    def SetCapacitance(self, e):
        temp = self.one.GetValue()
        #print (temp)
        Cset = str(temp)
        set_Cset = mmis.Functions.SETTransactions(0X05, Cset , self.chipselect, self.interruptpin)

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
