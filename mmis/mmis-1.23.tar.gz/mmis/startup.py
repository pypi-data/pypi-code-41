#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import wx
ImgFolder = '/home/pi/.local/lib/python3.5/site-packages/mmis/Images/'
#ImgFolder = '/usr/local/lib/python3.5/dist-packages/mmis/Images/' 
#ImgFolder = '/home/pi/Desktop/package/mmis/Images/'

class TabOne(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,parent,wx.ID_ANY,"Loading",size=(400,400), style=wx.DEFAULT_FRAME_STYLE^(~wx.CLOSE_BOX))
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Onclosewindow, self.redraw_timer) #Timer event occurs every few milliseconds that it was set 
        self.redraw_timer.Start(10000)
        self.Logo = wx.StaticBitmap(self, -1, pos = (50,50))
        self.image_file = ImgFolder+'MMIstart.png'
        self.Logo.SetFocus()
        self.Logo.SetBitmap(wx.Bitmap(self.image_file))
        
    def Onclosewindow(self, e):
        self.Destroy()

def StartTest():
    app1 = wx.App(None)
    frame1 = TabOne(None)
    frame1.Show()
    frame1.Centre()
    app1.MainLoop()
        
if __name__ == '__main__':
    StartTest()
