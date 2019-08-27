# -*- coding: utf-8 -*-

import win32api
import os
import sys
from pathlib import Path
from win32com.client import GetObject
from time import sleep
import shutil

import xlrd

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from keywords.GTFLibrary import Control


class PublicFunction:
    """加密锁设置"""
    def __init__(self):
        self.ctl = Control()
    
    def ConfigFindType(self, findtype):
        """
        设置加密锁查找方式
        :param findtype:
        :return:
        """
        if findtype == "自动查找加密锁":
            if self.ctl.Checked("自动查找加密锁", "RadioButton") == "False":
                self.ctl.ClickWW("自动查找加密锁", "RadioButton")
        elif findtype == "查找当前机器上的加密锁（单机锁、网络锁）":
            if self.ctl.Checked("指定查找加密锁", "RadioButton") == "False":
                self.ctl.ClickWW("指定查找加密锁", "RadioButton")
            if self.ctl.Checked("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox") == "False":
                self.ctl.ClickWW("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox")
            if self.ctl.Checked("查找同网段其他机器上的网络锁", "CheckBox") == "True":
                self.ctl.ClickWW("查找同网段其他机器上的网络锁", "CheckBox")
            if self.ctl.Checked("查找指定的网络授权", "CheckBox") == "True":
                self.ctl.ClickWW("查找指定的网络授权", "CheckBox")
        elif findtype == "查找同网段其他机器上的网络锁":
            if self.ctl.Checked("指定查找加密锁", "RadioButton") == "False":
                self.ctl.ClickWW("指定查找加密锁", "RadioButton")
            if self.ctl.Checked("查找同网段其他机器上的网络锁", "CheckBox") == "False":
                self.ctl.ClickWW("查找同网段其他机器上的网络锁", "CheckBox")
            if self.ctl.Checked("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox") == "True":
                self.ctl.ClickWW("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox")
            if self.ctl.Checked("查找指定的网络授权", "CheckBox") == "True":
                self.ctl.ClickWW("查找指定的网络授权", "CheckBox")
        elif findtype == "查找指定的网络授权":
            if self.ctl.Checked("指定查找加密锁", "RadioButton") == "False":
                self.ctl.ClickWW("指定查找加密锁", "RadioButton")
            if self.ctl.Checked("查找指定的网络授权", "CheckBox") == "False":
                self.ctl.ClickWW("查找指定的网络授权", "CheckBox")
            if self.ctl.Checked("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox") == "True":
                self.ctl.ClickWW("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox")
            if self.ctl.Checked("查找同网段其他机器上的网络锁", "CheckBox") == "True":
                self.ctl.ClickWW("查找同网段其他机器上的网络锁", "CheckBox")
        elif findtype == "查找当前机器上的加密锁+查找指定的网络授权":
            if self.ctl.Checked("指定查找加密锁", "RadioButton") == "False":
                self.ctl.ClickWW("指定查找加密锁", "RadioButton")
            if self.ctl.Checked("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox") == "False":
                self.ctl.ClickWW("查找当前机器上的加密锁（单机锁、网络锁）", "CheckBox")
            if self.ctl.Checked("查找指定的网络授权", "CheckBox") == "False":
                self.ctl.ClickWW("查找指定的网络授权", "CheckBox")
            if self.ctl.Checked("查找同网段其他机器上的网络锁", "CheckBox") == "True":
                self.ctl.ClickWW("查找同网段其他机器上的网络锁", "CheckBox")
        else:
            print("查找方式输入有误！")

    # 等待控件出现
    def WaitTimesUntilFlagIsFound(self, flag, controlName, times):
        """
        等待控件出现
        :param flag:
        :param controlName:
        :param times:
        :return:
        """
        times = int(times)
        t = 0
        while t <= times:
            if self.ctl.Find(flag, controlName) == "False":
                sleep(0.5)
                if t == times:
                    raise AssertionError("没有找到" + flag + controlName)  # 未找到控件，则停止继续运行
                t += 0.5
            else:
                break

    # 等待找到进程
    def WaitTimesUntilFindProc(self, procname, times):
        """
        等待找到进程
        :param procname:
        :param times:
        :return:
        """
        times = int(times)
        t = 0
        while t <= times:
            if self.ProcExist(procname) == False:
                sleep(0.5)
                if t == times:
                    raise AssertionError("没有找到" + procname)  # 未找到进程，则停止运行
                t += 0.5
            else:
                break

    # 查看进程是否存在，返回BOOL值
    def ProcExist(self, procname):
        """
        查看进程是否存在，返回BOOL值
        :param procname:
        :return:
        """
        is_exist = False
        wmi = GetObject('winmgmts:/root/cimv2')
        processCodeCov = wmi.ExecQuery('select * from Win32_Process where name=\"%s\"' % (procname))
        if len(processCodeCov) > 0:
            is_exist = True
        return is_exist

    
    def RunProc(self, procpath, CmdParam = ''):
        """
        启动进程
        :param procpath: 执行文件的路径
        :param CmdParam: 命令行参数，默认为空
        :return:
        """
        win32api.ShellExecute(0, 'open', procpath, CmdParam, '', 1)


    # 终止进程
    def KillProc(self, procname):
        """
        杀掉进程
        :param procname:
        :return:
        """
        try:
            if self.ProcExist(procname):
                os.system("taskkill /F /IM " + procname)
        except Exception as e:
            print("杀掉进程失败！")
            print(e)

    # 签收码读取
    def SignCode(self, filename, index):

        fname = filename.decode("utf-8")  # 文件名包含中文会报错，需要对文件名进行转码
        bk = xlrd.open_workbook(fname)  # 打开excel
 
        try:
            sh = bk.sheet_by_name("Sheet1")  # 获取sheet
        except:
            print("no sheet in %s named Sheet1" % fname)

        nrows = sh.nrows

        index = int(index)
        if index <= nrows:
            value = int(sh.cell_value(index, 1))  # 从0开始计数的
            return value
        else:
            raise AssertionError("没有更多的产品签收码了~")

    # 复制驱动文件到指定目录
    def CopyGSCFile(self, ProgramName, GSCVerion, DateTime):
        """
        复制驱动文件到指定目录
        :param ProgramName: 目前只能填写GSCSetup.exe和GSCTest.exe，若为GSCTest.exe，会将GSCTest.exe和GTFEngine.dll复制到新驱动安装目录下
        :param GSCVerion: 新驱动后2位版本号
        :param DateTime:驱动打版时间，如2019.02.21
        :return:
        """
        if ProgramName == "GSCSetup.exe":
            filedir_src = "\\\\server-rd\\granddog$\\" + DateTime + ".BUILD." + GSCVerion + "\\Driver\\GSCSetup.exe"
            filedir_dst = "G:\\GSCSetup\\GSCSetup-" + GSCVerion + ".exe"  # 路径不能是中文
            shutil.copy(filedir_src, filedir_dst)  # 将驱动复制到指定目录下，并重命名
        elif ProgramName == "GSCTest.exe":
            filedir_srca = "\\\\server-rd\\granddog$\\" + DateTime + ".BUILD." + GSCVerion + "\\Test\\GSCTest.exe"
            filedir_srcb = "G:\\GSCSetup\\GTFEngine.dll"
            filedir_dsta = "C:\\Program Files (x86)\\Common Files\\Grandsoft Shared\\GrandDog\\3.8." + GSCVerion + "\\GSCTest.exe"
            filedir_dstb = "C:\\Program Files (x86)\\Common Files\\Grandsoft Shared\\GrandDog\\3.8." + GSCVerion + "\\GTFEngine.dll"
            shutil.copy(filedir_srca, filedir_dsta)  # 将GSCTest工具复制到新驱动安装目录下
            shutil.copy(filedir_srcb, filedir_dstb)  # 将GTFEngine.dll文件复制到新驱动安装目录下
        else:
            print("程序名称输入错误！！")

if __name__ == '__main__':
    pass