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
DEVICES = {}
REFRESH_DEVICES = {}
CURRENT_SELECT_DEVICE_INDEX = 0
CURRENT_SELECT_PACKAGE_INDEX = 0

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

        wx.Frame.__init__(self,None,size=(800,600),title='XYMonkey')

        # 工作路径
        wx.StaticText(self,-1,pos=(15,15),label='工作目录:')
        self.workspace_text = wx.TextCtrl(self,-1,pos=(80,10),size=(300,30))
        self.select_workspace = wx.Button(self,-1,label="选择",pos=(400,10),size=(50,30),style = wx.TE_READONLY)

        # 周期(h)
        wx.StaticText(self,-1,pos=(15,60),label='周期(h):')
        self.cycle = wx.SpinCtrl(self, -1, "", (80, 55), (100, 30))  
        self.cycle.SetRange(1,100)  

        # 循环次数
        wx.StaticText(self,-1,pos=(190,60),label='循环次数:')
        self.run_times = wx.SpinCtrl(self, -1, "", (260, 55), (100, 30))  
        self.run_times.SetRange(1,100)  

        # 动作延迟(ms)
        wx.StaticText(self,-1,pos=(370,60),label='动作延迟(ms):')
        self.delay = wx.SpinCtrl(self, -1, "", (470, 55), (100, 30))  
        self.delay.SetRange(1,10000)

        # 总耗时(h)
        wx.StaticText(self,-1,pos=(580,60),label='总耗时(h):')
        self.total_time = wx.SpinCtrl(self, -1, "", (670, 55), (100, 30))  
        self.total_time.SetRange(1,100)  

        # 单次执行次数
        wx.StaticText(self,-1,pos=(15,100),label='单次执行次数:')
        self.times_in_one = wx.StaticText(self,-1,pos=(125,100),label='')

        # 种子数
        wx.StaticText(self,-1,pos=(15,140),label='种子数:')
        self.seed_num = wx.SpinCtrl(self, -1, "", (110, 135), (100, 30))  
        self.seed_num.SetRange(1,10000)

        # 日志等级
        wx.StaticText(self,-1,pos=(15,180),label='日志等级:')
        self.log_level = wx.Choice(self,-1,(110,170),(100, 40))

        # 运行模式

        # 刷新
        self.refresh_btn = wx.Button(self,-1,label='刷新',pos=(20,250),size=(50,30))
        # 手机
        sampleList = []  
        wx.StaticText(self, -1, "设备及应用:", (15, 220),(100,30))  
        self.devices = wx.CheckListBox(self, -1, (110, 220),(300,180),style=1)  

        # 包筛选
        self.package_screen_str = wx.TextCtrl(self,-1,pos=(450,220),size=(230, 25))
        self.screen_btn = wx.Button(self,-1,label="过滤",pos=(700,220),size=(50,30))

        # 应用
        sampleList = []  
        self.packages = wx.CheckListBox(self, -1, (450, 250),(300,150), choices=sampleList)  

        # 日志
        # wx.StaticText(self,-1,pos=(430,95),label='日志:')
        # self.log_str = wx.TextCtrl(self,-1,pos=(480,95),size=(300,300))

        # 进度条
        # wx.StaticText(self,-1,label='当前周期进度:',pos=(650,430),size=(85,30))
        self.process_bar = wx.StaticText(self,-1,label='当前周期进度:0/100 %',pos=(15,430),size=(85,30))
        self.count = 0  
        self.gauge = wx.Gauge(self, -1, 50, pos=(20, 440), size=(760, 25))  
        self.gauge.SetBezelFace(3)  
        self.gauge.SetShadowWidth(3)  

        # 总进度条
        self.count = 0 
        self.total_process_bar = wx.StaticText(self,-1,label='当前周期:0/100',pos=(15,470),size=(85,30))
        self.total_gauge = wx.Gauge(self, -1, 50, (20, 480), (760, 25))  
        self.total_gauge.SetBezelFace(3)  
        self.total_gauge.SetShadowWidth(3)  

        # 取消 确定
        self.cancel_btn = wx.Button(self,-1,label="取消",pos=(660,520),size=(50,30))
        self.confirm_btn = wx.Button(self,-1,label="开始",pos=(730,520),size=(50,30))

        # 赋值
        self.set_default_for_UI()

        # 事件绑定
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.select_workspace) #文件夹
        self.screen_btn.Bind(wx.EVT_BUTTON,self.screen_btn_click)
        self.cycle.Bind(wx.EVT_SPINCTRL,self.change_cycle)
        self.cycle.Bind(wx.EVT_TEXT,self.change_cycle)
        self.run_times.Bind(wx.EVT_SPINCTRL,self.change_runtimes)
        self.run_times.Bind(wx.EVT_TEXT,self.change_runtimes)

        self.delay.Bind(wx.EVT_SPINCTRL,self.change_delay)
        self.delay.Bind(wx.EVT_TEXT,self.change_delay)

        self.total_time.Bind(wx.EVT_SPINCTRL,self.change_total_time)
        self.total_time.Bind(wx.EVT_TEXT,self.change_total_time)

        self.seed_num.Bind(wx.EVT_SPINCTRL,self.change_seed) #种子数
        self.seed_num.Bind(wx.EVT_TEXT,self.change_seed)

        self.log_level.Bind(wx.EVT_CHOICE,self.One_Play) #日志等级

        self.refresh_btn.Bind(wx.EVT_BUTTON,self.refresh_btn_click)
        self.devices.Bind(wx.EVT_CHECKLISTBOX,self.change_devices_and_packages)
        self.packages.Bind(wx.EVT_CHECKLISTBOX,self.change_devices_and_packages)

        # self.gauge.Bind(wx.EVT_IDLE, self.OnIdle)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Centre()
        self.Show(True)

        self.confirm_btn.Bind(wx.EVT_BUTTON,self.start_monkey)
        self.cancel_btn.Bind(wx.EVT_BUTTON,self.cancel_monkey)


    # {"vivo_vivo X3V_d934619c":{'is_check':false,'packages':[{name:com.xxx.xxx,is_check:true}]}}
    # {"vivo_vivo X3V_d934619c": ["com.saicmobility.user", "com.saicmobility.lease.driver"]}
    def start_monkey(self,event):
        global DEVICES
        devices = {}
        for key,value in DEVICES.items():
            packages = []
            if value['is_check'] :
                for package in value['packages']:
                    if package['is_check'] :
                        packages.append(package['name'])
                devices[key] = packages
        ui.set_config_with_name('mobile',devices)
        Test().setup_task_files(ui)
        Test().run_monkey_with_config(ui,self.change_process)

    def cancel_monkey(self,event):
        Test().stop_test(ui)

    def change_process(self,current,cycle):
        cycles = ui.get_config_with_name('cycles')
        cycle_str = '('+ cycle + '/' + cycles +')'
        cycle_time = ui.get_config_with_name('life_cycle')
        cycle_process = round(current / cycle_time * 60 * 60 * 100 /cycles, 2)  +  cycle * 25
        self.total_process_bar.SetLabelText('当前进度: ' + cycle_process + '%')
        self.gauge.SetValue(cycle_process)
 
    def change_devices_and_packages(self,event):
        global DEVICES,CURRENT_SELECT_DEVICE_INDEX,CURRENT_SELECT_PACKAGE_INDEX
        mobile_checks = list(self.devices.GetCheckedItems())
        package_checks = list(self.packages.GetCheckedItems())

        if event.GetEventObject() is self.devices:
            index = self.differ_devices()
            CURRENT_SELECT_DEVICE_INDEX = index
            self.change_devices_check_status()
            print('点击了设备index:' + str(index))
        elif event.GetEventObject() is self.packages:
            index = self.differ_packages()
            CURRENT_SELECT_PACKAGE_INDEX = index
            self.change_devices_check_status()
            print('点击了包index:' + str(index))

    def differ_packages(self):
        global DEVICES,CURRENT_SELECT_DEVICE_INDEX,CURRENT_SELECT_PACKAGE_INDEX
        package_checks = list(self.packages.GetCheckedItems())
        index = 0
        packages = []
        for key,value in DEVICES.items():
            if CURRENT_SELECT_DEVICE_INDEX == index:
                packages = value['packages']
                break
            index = index + 1
        # print(packages)
        package_index = 0
        for package in packages:
            if package['is_check'] and not self.packages.IsChecked(package_index):
                return package_index
            elif not package['is_check'] and self.packages.IsChecked(package_index):
                return package_index
            package_index = package_index + 1
        return None

    def change_devices_check_status(self):
        global DEVICES,CURRENT_SELECT_DEVICE_INDEX,CURRENT_SELECT_PACKAGE_INDEX
        index = 0
        mobile = self.devices.IsChecked(CURRENT_SELECT_DEVICE_INDEX)
        package = self.packages.IsChecked(CURRENT_SELECT_DEVICE_INDEX)
        for key,value in DEVICES.items():
            if index == CURRENT_SELECT_DEVICE_INDEX:
                if mobile is not None:
                    value['is_check'] = mobile
                
                if package is not None:
                    packages = value['packages']
                    package_b = packages[CURRENT_SELECT_PACKAGE_INDEX]
                    package_b['is_check'] = self.packages.IsChecked(CURRENT_SELECT_PACKAGE_INDEX)
                    # print(package_b)
                return

            index = index + 1
        # print(package)

    def differ_devices(self):
        global DEVICES
        mobile_checks = list(self.devices.GetCheckedItems())
        index = 0
        for key,value in DEVICES.items():
            if value['is_check'] and not self.devices.IsChecked(index):
                return index
            elif not value['is_check'] and self.devices.IsChecked(index):
                return index
            index = index + 1
        return None


    def change_seed(self,e):
        seed_num = self.seed_num.GetValue()
        ui.set_config_with_name('seed_num',seed_num)

    def change_delay(self,event):
        delay = self.delay.GetValue()
        ui.set_config_with_name('time_delay',delay)
        self.change_cycle(None)
        # self.total_time.SetValue(cycle*self.run_times.GetValue())

    def change_total_time(self,event):
        time_use = self.total_time.GetValue()
        cycles = time_use/self.cycle.GetValue()
        self.run_times.SetValue(cycles)
        ui.set_config_with_name('cycles',int(cycles))

    def change_cycle(self,event):
        cycle = self.cycle.GetValue()
        delay = self.delay.GetValue()
        ui.set_config_with_name('life_cycle',cycle)
        self.total_time.SetValue(cycle*self.run_times.GetValue())
        times_in_one = cycle*60*60*1000/delay
        self.times_in_one.SetLabelText(str(int(times_in_one)))
        ui.set_config_with_name('run_times',int(times_in_one))
        # print(self.cycle.GetValue())

    def change_runtimes(self,event):
        runtimes = self.run_times.GetValue()
        ui.set_config_with_name('cycles',int(runtimes))
        self.total_time.SetValue(runtimes*self.cycle.GetValue())

    def OnPaint(self, e): 
      dc = wx.PaintDC(self)
      brush = wx.Brush("#C0C0C0")
      dc.SetBackground(brush) 
      dc.Clear()
		
      font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL) 
      dc.SetFont(font) 
      pen = wx.Pen(wx.Colour(105,105,105)) 
      dc.SetPen(pen) 
      dc.DrawLine(15,47,770,47) 
      dc.DrawLine(15,130,770,130)
      dc.DrawLine(15,130,770,130)

    def set_default_for_UI(self):
        global LOG_LEVEL
        self.workspace_text.SetLabelText(ui.get_config_with_name('workspace'))

        # 种子数
        self.seed_num.SetValue(ui.get_config_with_name('seed_num')) 
        # 周期
        self.cycle.SetValue(ui.get_config_with_name('life_cycle')) 
        # 循环次数
        self.run_times.SetValue(ui.get_config_with_name('cycles')) 
        # 动作延迟
        self.delay.SetValue(ui.get_config_with_name('time_delay'))
        self.change_cycle(None)
        if ui.get_config_with_name('screen_key') is not None and len(ui.get_config_with_name('screen_key')) > 0:
            self.package_screen_str.SetValue(ui.get_config_with_name('screen_key'))
        
        self.total_time.SetValue(self.cycle.GetValue()*self.run_times.GetValue())
        # 日志等级
        self.log_level.AppendItems(list(LOG_LEVEL.keys()))
        # 筛选关键字
        self.refresh_device(True)

    
    def refresh_btn_click(self,e):
        self.refresh_device(True)

    def screen_btn_click(self,event):
        self.refresh_device(False)

    def refresh_device(self,is_first=False):
        global DEVICES,CURRENT_SELECT_DEVICE_INDEX
        if is_first:
            ui.set_config_with_name('screen_key','')
            self.package_screen_str.SetValue('')
        else:
            ui.set_config_with_name('screen_key',self.package_screen_str.GetValue())
       
        screen_word = self.package_screen_str.GetValue()

        mobile = ui.get_all_devices(screen_word)
        keys = list(mobile.keys())
        self.devices.SetItems(keys)
        packages = []
        if len(keys) > 0:
            packages = mobile[keys[CURRENT_SELECT_DEVICE_INDEX]]
            self.packages.SetItems(packages)
        # print(packages)

        if is_first:
            for key,value in mobile.items():
                device = {}
                device['is_check'] = False
                packages = [] 
                for package in value:
                    package_t = {'name':package,'is_check':False}
                    packages.append(package_t)
                device['packages'] = packages
                DEVICES[key] = device

        else:
            index = 0
            select_array = []
            for key,value in DEVICES.items():
                if value['is_check'] == True:
                    select_array.append(key)
                if index == CURRENT_SELECT_DEVICE_INDEX:
                    package_select_array = []
                    package_device_array = []
                    for package in packages:
                        real_package = {'name':package}
                        for package_1 in value['packages']:
                            if package == package_1['name']:
                                print(package_1)
                                if package_1['is_check']:
                                    real_package['is_check'] = True
                                    package_select_array.append(package)
                                else:
                                    real_package['is_check'] = False
                                break
                        package_device_array.append(real_package)

                    self.packages.SetCheckedStrings(package_select_array)
                    value['packages'] = package_device_array
                    # print(DEVICES)
                    break
                
                index = index + 1  
            self.devices.SetCheckedStrings(select_array)

            # 包设置选中状态


    # def OnIdle(self, event):  
    #     self.count = self.count + 1  
    #     if self.count  == 50:  
    #         self.count = 0 
    #     self.gauge.SetValue(self.count)  

    def One_Play(self,event):
        log_level = LOG_LEVEL[event.GetString()]
        ui.set_config_with_name('log_level',log_level)


    def OnButton(self, event):
        dlg = wx.DirDialog(self,u"选择文件夹",style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.workspace_text.SetLabelText(dlg.GetPath() + '/')
            ui.set_config_with_name('workspace',dlg.GetPath() + '/')
        dlg.Destroy()



if __name__ == '__main__':
    frame = wx.App()
    app = MonkeyFrame()
    app.Show()
    frame.MainLoop()