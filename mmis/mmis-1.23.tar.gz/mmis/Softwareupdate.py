#!/usr/bin/env python3
import subprocess
import sys
import os, fnmatch
import wx
import urllib.request

#results = find(pattern, path)

class USB(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,parent,wx.ID_ANY,"Check Updates",size=(400,230), style=wx.DEFAULT_FRAME_STYLE)

        self.path = '/media'
        self.pattern = '*.tar.gz'
        self.cmd = 'pip3 install '

        self.redraw_timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.find, self.redraw_timer1) #Timer event occurs every few milliseconds that it was set 

        self.redraw_timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.checkonlineupdate, self.redraw_timer2)
        self.redraw_timer2.Start(1000)

        self.font1 = wx.Font(18, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.font2 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')

        #self.lblname = wx.StaticText(self, label = "Checking in progress.......", pos = (40,45))
        #self.lblname.SetFont(self.font1)

        self.lblname1 = wx.StaticText(self, label = "Checking online update", pos = (80,105))
        self.lblname1.SetFont(self.font1)

    def checkonlineupdate(self, e):
        try:
                self.redraw_timer2.Stop()
                urllib.request.urlopen("http://www.google.com")
                status = "Connected"
                self.lblname1.Destroy()
                onlineversion = os.popen('pip3 search mmis').read()
                onlineversion = float(onlineversion[6:10])

                self.local = os.popen('pip3 show mmis | grep Version').read()
                if len(self.local) == 0:
                    self.local = 'not found'
                    self.currentversion = 0.0
                else:
                    self.currentversion = float(self.local[9:13])

                if (onlineversion <= self.currentversion):
                    self.lblname1 = wx.StaticText(self, label = "already upto date", pos = (80,105))
                    self.lblname1.SetFont(self.font1)
                else:
                    self.lblname1 = wx.StaticText(self, label = "online update found", pos = (80,105))
                    self.lblname1.SetFont(self.font1)

                currentversioninstalled = "existing installer "+ self.local
                self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
                self.lblname0.SetFont(self.font1)
                self.lblname = wx.StaticText(self, label = "Version available:", pos = (20,65))
                self.lblname.SetFont(self.font2)
                self.version = wx.TextCtrl(self, size=(150,30), pos = (200,60), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
                self.version.SetValue(str(onlineversion))

                self.button1 = wx.Button(self, label="Update", pos=(170, 150), size = (200,40), id = -1)
                self.button1.SetFont(self.font2)
                self.button1.Bind(wx.EVT_BUTTON, self.ON_onlineupdate)
                self.button1.SetForegroundColour('black')
                self.button1.SetBackgroundColour(wx.Colour(211,211,211))
                
        except:
                self.lblname1.Destroy()
                self.lblname1 = wx.StaticText(self, label = "Internet connection not found \n looking for updates from external drive", pos = (30,65))
                self.lblname1.SetFont(self.font2)
                status = "Not connected"
                self.redraw_timer1.Start(1000)

    def find(self, e):
        self.redraw_timer1.Stop()

        self.local = os.popen('pip3 show mmis | grep Version').read()
        if len(self.local) == 0:
            self.local = 'not found'
            self.currentversion = 0.0
        else:
            self.currentversion = float(self.local[9:13])
            
        self.result = []
        for root, dirs, files in os.walk(self.path):
            for name in files:
                if fnmatch.fnmatch(name, self.pattern):
                    self.result.append(os.path.join(root, name))

        self.mmis = [s for s in self.result if 'mmis-' in s]
        self.lblname1.Destroy()
        
        if (len(self.mmis)>0):
            #self.lblname.Destroy()
            self.mmis.sort()
            self.latestversion = self.mmis[len(self.mmis)-1]
            
            version = self.latestversion[(len(self.latestversion)-11):]
            version = float(version[:4])

            if (version <= self.currentversion):
                self.lblname1 = wx.StaticText(self, label = "already upto date", pos = (80,105))
                self.lblname1.SetFont(self.font1)
            else:
                self.lblname1 = wx.StaticText(self, label = "Click to update", pos = (80,105))
                self.lblname1.SetFont(self.font1)
            
            currentversioninstalled = "existing installer "+ self.local
            self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
            self.lblname0.SetFont(self.font1)
            self.lblname = wx.StaticText(self, label = "Version available:", pos = (20,65))
            self.lblname.SetFont(self.font2)
            self.version = wx.TextCtrl(self, size=(150,30), pos = (200,60), style = wx.TE_NO_VSCROLL|wx.TE_LEFT|wx.TE_READONLY)
            self.version.SetValue(str(version))
            
            self.button = wx.Button(self, label="Update", pos=(170, 150), size = (200,40), id = -1)
            self.button.SetFont(self.font2)
            self.button.Bind(wx.EVT_BUTTON, self.ON_update)
            self.button.SetForegroundColour('black')
            self.button.SetBackgroundColour(wx.Colour(211,211,211))
            
        else:
            #self.lblname.Destroy()
            self.lblname0 = wx.StaticText(self, label = "pendrive not found", pos = (20,15))
            self.lblname0.SetFont(self.font1)

    def ON_update(self, e):
        self.lblname1.Destroy()
        self.cmd = self.cmd + self.latestversion
        os.system(self.cmd)
        self.lblname1 = wx.StaticText(self, label = "Updated successfully", pos = (80,105))
        self.lblname1.SetFont(self.font1)
        
        self.lblname0.Destroy()
        self.local = os.popen('pip3 show mmis | grep Version').read()
        currentversioninstalled = "existing installer "+ self.local
        self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
        self.lblname0.SetFont(self.font1)

    def ON_onlineupdate(self, e):
        self.lblname1.Destroy()
        os.system('pip3 install mmis')
        self.lblname1 = wx.StaticText(self, label = "Updated successfully", pos = (80,105))
        self.lblname1.SetFont(self.font1)

        self.lblname0.Destroy()
        self.local = os.popen('pip3 show mmis | grep Version').read()
        currentversioninstalled = "existing installer "+ self.local
        self.lblname0 = wx.StaticText(self, label = currentversioninstalled, pos = (20,15))
        self.lblname0.SetFont(self.font1)


def StartTest():
    app1 = wx.App(None)
    frame1 = USB(None)
    frame1.Show()
    frame1.Centre()
    app1.MainLoop()
        
if __name__ == '__main__':
    StartTest()
