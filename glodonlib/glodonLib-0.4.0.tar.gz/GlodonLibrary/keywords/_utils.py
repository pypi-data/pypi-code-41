# coding:utf-8
import json
import winreg
import datetime
import time
import base64
import os


class BaseFunc(object):
    
    def update_json(self, url, *parameters):
        """读取配置文件里的信息，拼接后转换为json格式"""
        if url == 'nourl':
            json_Str = "{}"
        else:
            json_Str = open(url).read()
        json_Str = json_Str.replace('\t', '').replace('\n', '')
        jsonStr = json.loads(json_Str)
        strDict = 'jsonStr'
        for parameter in parameters:
            print((strDict + parameter))
            try:
                exec (strDict + parameter)
            except:
                print('Expression execute failed![', strDict + parameter, ']')
        return json.dumps(jsonStr)
    
    def get_uuid(self,key=winreg.HKEY_LOCAL_MACHINE, sub_key=r'Software\Wow6432Node\Glodon\GDP\2.0'):
        """
        读取注册表信息，获取设备ID。
        :param key: 注册表主目录，默认为HKEY_LOCAL_MACHINE
        :param sub_key: 注册表从目录，默认Software\Wow6432Node\Glodon\GDP\2.0。
        :return: 设备ID(uuid)
        """
        return winreg.QueryValueEx(winreg.OpenKey(key, sub_key),'guid')[0].encode('utf-8')

    def get_verison(self, key=winreg.HKEY_LOCAL_MACHINE, sub_key=r'Software\Wow6432Node\Glodon\GDP\2.0'):
        """
        读取注册表信息，获取版本号。
        :param key: 注册表主目录，默认为HKEY_LOCAL_MACHINE
        :param sub_key: 注册表从目录，默认Software\Wow6432Node\Glodon\GDP\2.0。
        :return: version
        """
        return winreg.QueryValueEx(winreg.OpenKey(key, sub_key), 'Version')[0].encode('utf-8')


    def AfterDaysLocalTime(self, days, ntype):
        """
        获取xx天后的时间
        :param period: days 相隔的天数
        :param ntype: 必须为int类型，1返回时间格式："%Y-%m-%d %H:%M"，2返回时间格式："%Y年%m月%d日"
        :return:
        """
        t = time.localtime()
        # 第二年若为闰年，参数的天数加1
        year = t.tm_year
        days = int(days)
        if days/365:
            year = t.tm_year + 1
        if t.tm_mon > 2:
            if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
                days = days + 1

        if ntype == '1':
            return (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H")
        elif ntype == '2':
            return (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y年%m月%d日")
        else:
            raise ValueError('ntype赋值错误！')

    def SetRegValue(self, ValueName, ValueContent, subkey="SOFTWARE\\Wow6432Node\\GrandSoft\\GrandDog\\3.0\\Server",winregType =winreg.REG_SZ, key=winreg.HKEY_LOCAL_MACHINE):
        """
        设置注册表值，不存在的会先创建
        :param ValueName:
        :param ValueContent:
        :param winregType: 默认值：_winreg.REG_SZ   #在robot中REG_SZ为1，REG_DWORD为4
        :param key:默认值：HKEY_LOCAL_MACHINE
        :param subkey:默认值：SOFTWARE\\Wow6432Node\\GrandSoft\\GrandDog\\3.0\\Server
        :return:
        """
        if winregType == 4:
            ValueContent = int(ValueContent)

        winreg.SetValueEx(
            winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS),
            ValueName,
            0,
            winregType,
            ValueContent
        )

    # 注册表中删除键
    def DeleteRegValue(self, ValueName, subkey="SOFTWARE\\Wow6432Node\\GrandSoft\\GrandDog\\3.0\\Server", key=winreg.HKEY_LOCAL_MACHINE ):
        """
        注册表中删除键，不存在的删除失败，吃掉异常
        :param ValueName:
        :param key:默认值：HKEY_LOCAL_MACHINE
        :param subkey:默认为：SOFTWARE\\Wow6432Node\\GrandSoft\\GrandDog\\3.0\\Server
        :return:
        """
        try:
            winreg.DeleteValue(winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS), ValueName)
        except Exception as e:
            print("没有键值")
            print(e)

    # 获取账号对应密码
    def GetPassword(self, Account):
        """
        获取账号对应密码
        :param Account:
        :return:
        """
        if Account == "zhaofy":
            Password = base64.b64decode('MXFhekBXU1g=')
            return Password
        else:
            print(("没有账号" + Account + "对应的密码！"))

    def DeleteFile(self, FileName):
        """
        删除文件
        :param FileName:
        :return:
        """
        try:
            if os.access(FileName, os.F_OK):
                os.remove(FileName)
        except Exception as e:
            print("无法删除")
            print(e)
            # raise e

    def ExistFile(self,FileName):
        """
        判断文件是否存在
        :param FileName:
        :return:
        """
        if os.access(FileName, os.F_OK):
            return True
        else:
            return False
