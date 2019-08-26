#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: XYCoder
# FILE: ~/Desktop/saic/xyscript/xyscript/test/testUI.py
# DATE: 2019/08/21 Wed
# TIME: 17:48:04

# DESCRIPTION:测试模块UI部分

# Tkinter  :是python最简单的图形化模块，总共只有14种组建
# Pyqt     :是python最复杂也是使用最广泛的图形化
# Wx       :是python当中居中的一个图形化，学习结构很清晰
# Pywin    :是python windows 下的模块，摄像头控制(opencv)，常用于外挂制作

import wx
import time,os
from xyscript.test.test import Test,TestUI

LOG_LEVEL = {'简单':' -v','普通':' -v -v','详细':' -v -v -v'}

ui = TestUI()

class MonkeyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.setup_main_window()
        self.panel = wx.Panel(self) 

    def setup_main_window(self):
        # 初始化菜单按钮
        menuBar = wx.MenuBar()
        menu1 = wx.Menu("test")
        menuBar.Append(menu1, "File")
        self.SetMenuBar(menuBar)

        wx.Frame.__init__(self,None,size=(800,550),title='XYMonkey')

        self.SetOwnBackgroundColour("#C0C0C0")

        # 工作路径
        wx.StaticText(self,-1,pos=(15,15),label='工作目录:')
        self.workspace_text = wx.TextCtrl(self,-1,pos=(80,10),size=(300,30))
        self.select_workspace = wx.Button(self,-1,label="选择",pos=(400,10),size=(50,30),style = wx.TE_READONLY)

        # 周期(h)
        wx.StaticText(self,-1,pos=(15,60),label='周期(h):')
        self.cycle = wx.SpinCtrl(self, -1, "", (80, 55), (100, 30))  
        self.cycle.SetRange(1,100)  
        self.cycle.SetValue(4) 

        # 循环次数
        wx.StaticText(self,-1,pos=(190,60),label='循环次数:')
        self.run_times = wx.SpinCtrl(self, -1, "", (260, 55), (100, 30))  
        self.run_times.SetRange(1,100)  
        self.run_times.SetValue(3) 

        # 动作延迟(ms)
        wx.StaticText(self,-1,pos=(370,60),label='动作延迟(ms):')
        self.delay = wx.SpinCtrl(self, -1, "", (470, 55), (100, 30))  
        self.delay.SetRange(1,10000)  
        self.delay.SetValue(400) 

        # 总耗时(h)
        wx.StaticText(self,-1,pos=(580,60),label='总耗时(h):')
        self.total_time = wx.SpinCtrl(self, -1, "", (670, 55), (100, 30))  
        self.total_time.SetRange(1,100)  
        self.total_time.SetValue(12) 

        # 单次执行次数
        wx.StaticText(self,-1,pos=(15,100),label='单次执行次数:')
        self.times_in_one = wx.SpinCtrl(self, -1, "", (110, 95), (100, 30))  
        self.times_in_one.SetRange(1,1000000)  
        self.times_in_one.SetValue(100000) 

        # 种子数
        wx.StaticText(self,-1,pos=(15,140),label='种子数:')
        self.seed_num = wx.SpinCtrl(self, -1, "", (110, 135), (100, 30))  
        self.seed_num.SetRange(1,10000)  
        self.seed_num.SetValue(800) 

        # 日志等级
        wx.StaticText(self,-1,pos=(15,180),label='日志等级:')
        self.log_level = wx.Choice(self,-1,(110,170),(100, 40),DateHandler().get_log_level())
        # self.log_level.Bind(wx.EVT_CHOICE,self.One_Play)


        # 运行模式

        # 手机
        sampleList = []  
        wx.StaticText(self, -1, "设备及应用:", (15, 220),(100,200))  
        self.devices = wx.CheckListBox(self, -1, (110, 220), choices=sampleList)  

        # 包筛选
        self.package_screen_str = wx.TextCtrl(self,-1,pos=(280,220),size=(130, -1))

        # 应用
        sampleList = ['zero', 'one', 'two', 'three', 'four', 'five',  
                      'six', 'seven', 'eight']  
        self.packages = wx.CheckListBox(self, -1, (280, 250), choices=sampleList)  

        # 日志
        wx.StaticText(self,-1,pos=(430,95),label='日志:')
        self.log_str = wx.TextCtrl(self,-1,pos=(480,95),size=(300,300))

        # 进度条
        self.count = 0  
        self.gauge = wx.Gauge(self, -1, 50, (20, 420), (760, 25))  
        self.gauge.SetBezelFace(3)  
        self.gauge.SetShadowWidth(3)  

        # 取消 确定
        self.cancel_btn = wx.Button(self,-1,label="取消",pos=(660,480),size=(50,30),style = wx.TE_READONLY)
        self.confirm_btn = wx.Button(self,-1,label="开始",pos=(730,480),size=(50,30),style = wx.TE_READONLY)

        # 赋值
        self.set_default_for_UI()

        # 事件绑定
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.select_workspace)

        self.Bind(wx.EVT_IDLE, self.OnIdle) 

    def set_default_for_UI(self):
        self.workspace_text.SetLabelText(ui.get_config_with_name('workspace'))

        mobile = ui.get_all_devices('saic')
        print(mobile)
        self.devices.AppendItems(mobile)


    def OnIdle(self, event):  
        self.count = self.count + 1  
        if self.count  == 50:  
            self.count = 0 
        self.gauge.SetValue(self.count)  


    def OnButton(self, event):
        dlg = wx.DirDialog(self,u"选择文件夹",style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            print (dlg.GetPath()) #文件夹路径
            self.workspace_text.SetLabelText(dlg.GetPath() + '/')
            ui.set_config_with_name('workspace',dlg.GetPath() + '/')
        dlg.Destroy()


class DateHandler():
    def get_log_level(self):
        global LOG_LEVEL
        log_level = []
        for key,value in LOG_LEVEL.items():
            log_level.append(key)
        return log_level
    
    def get_log_level_str(self,index):
        pass



if __name__ == '__main__':
    frame = wx.App()
    app = MonkeyFrame()
    app.Show()
    frame.MainLoop()