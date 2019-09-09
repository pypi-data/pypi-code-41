'''
Created on Mar 25, 2019

@author: hammonds
'''
import  wx
import  wx.lib.scrolledpanel as scrolled
from minixs.gui.image_view import ImageView

class TestPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        desc = wx.StaticText(self, -1,
                            "ScrolledPanel extends wx.ScrolledWindow, adding all "
                            "the necessary bits to set up scroll handling for you.\n\n"
                            "Here are three fixed size examples of its use. The "
                            "demo panel for this sample is also using it -- the \nwxStaticLine "
                            "below is intentionally made too long so a scrollbar will be "
                            "activated."
                            )
        desc.SetForegroundColour("Blue")
        vbox.Add(desc, 0, wx.ALIGN_LEFT|wx.ALL, 5)
      
        self.SetSizer(vbox)
        self.SetAutoLayout(1)
        self.SetupScrolling()
app = wx.App(0)
frame = wx.Frame(None, wx.ID_ANY)
fa = ImageView(frame)
frame.Show()
app.MainLoop()