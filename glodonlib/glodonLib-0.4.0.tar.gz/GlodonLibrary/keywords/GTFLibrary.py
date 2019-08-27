# -*-coding:utf-8 -*-
import http.client
from urllib.parse import quote


class GTFCodeMessage:
    """自动化消息映射单元"""
    
    dict = {-1: '异常', 0: '未赋值', 1: '成功返回', 2:'成功', 3:'窗体弹出', 4:'解析错误',5: '查找失败',
            6: '结果不唯一', 7: '其他错误', 8: '未知错误', 9: '非预期窗体', 10: '前节点执行异常'
            }
    
    @classmethod
    def _get_message_by_code(cls, code):
        return cls.dict.get(code, "errorcode:{0}".format(code))

class HttpConnection:
    """自动化测试框架通信类"""

    def __init__(self, ip="127.0.0.1", port='4440'):
        self.ip = ip
        self.port = port
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "Keep-Alive"
        }
        self.conn = http.client.HTTPConnection("{0}:{1}".format(self.ip, self.port))
        # self.codemessage = GTFCodeMessage()
    
    def GET(self, aurl, adata):
        self.conn.request(method="GET", url=quote(aurl), body=adata, headers=self.headers)
        response = self.conn.getresponse()
        content = response.read()
        status = response.status
        if status >= 510:
            status = status - 510
            raise Exception(GTFCodeMessage._get_message_by_code(status))

        else:
            status = status - 210
            print(GTFCodeMessage._get_message_by_code(status))
            return GTFCodeMessage._get_message_by_code(status), content
    
    def __del__(self):
        self.conn.close()


class _BaseControl(object):
    """基础控件自动化封装"""
    
    flag = ""
    flag_1 = ""
    flag_2 = ""
    control_path = "/{0}?{1}{2}$"
    control_Name = ""

    cmdClick = "{0}Click()"    # Button,CheckBox,RadioButton
    cmdClickWW = "{0}Click()?PopupWindow="""  # 点击按钮弹出窗体PW
    cmdClose = "{0}Close()"    # From
    cmdDbClick = "{0}DbClick()"
    cmdDbLClickWW = "{0}DbLClick({1})?PopupWindow="""
    cmdRightClick = "{0}RightClick()"
    cmdSetText = '{0}SetText({1})'   # Label,Edit,ComboBox
    cmdSetTextWW = '{0}SetText({1})?PopupWindow='  # 设置文本后弹出窗体
    cmdGetCount = '{0}GetCount()'  # ListView
    cmdGetText = '{0}GetText()'     # Edit,ComboBox
    cmdChecked = "{0}Checked()"      # radiobutton,checkbox
    cmdFind = "{0}Find()"
    cmdEnabled = "{0}Enabled()"
    cmdSelect = '{0}Select({1})'      # ListView
    cmdSelectbyIndex = '{0}SelectbyIndex({1})'  # ListView
    cmdSelected = "{0}Selected()"       # ListView

    def __init__(self, flag, controlName):
        self.connection = HttpConnection()
        self.flag = flag
        self.control_Name = controlName
        self.path = self._get_control_path()
        
    def _get_control_path(self):
        if self.flag.find("#") > -1:
            self.flag_1 = ""
            self.flag_2 = self.flag
        else:
            self.flag_1 = self.flag
            self.flag_2 = ""
        # path = self.control_path.format(self.flag_1, self.__class__.__name__, self.flag_2)
        path = self.control_path.format(self.flag_1, self.control_Name, self.flag_2)
        return path

    def BaseClick(self):
        """Button,CheckBox,RadioButton等控件的点击操作"""
        status, content = self.connection.GET(self.cmdClick.format(self.path), "")

    def BaseClickWW(self):   #点击后等待弹出窗体
       
        status, content = self.connection.GET(self.cmdClickWW.format(self.path), "")

    def BaseClose(self):
        
        status, content = self.connection.GET(self.cmdClose.format(self.path), "")

    def BaseDbClick(self):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdDbClick.format(self.path), "")

    def BaseDbLClickWW(self, LineName):    #选中x行双击，等待窗体弹出

        status, content = self.connection.GET(self.cmdDbLClickWW.format(self.path, LineName), "")

    def BaseRightClick(self):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdRightClick.format(self.path), "")

    def BaseSetText(self, text):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdSetText.format(self.path, text), "")
        return content

    def BaseSetTextWW(self, text):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdSetTextWW.format(self.path, text), "")
        return content

    def BaseGetCount(self):     #  'ListView自动化控件封装，目前只能通过#1，#2，#3按顺序去找'
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdGetCount.format(self.path), "")
        return content

    def BaseGetText(self):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdGetText.format(self.path), "")
        return content

    def BaseChecked(self):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdChecked.format(self.path), "")
        return content

    def BaseFind(self):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdFind.format(self.path), "")
        return content

    def BaseEnabled(self):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdEnabled.format(self.path), "")
        return content

    def BaseSelect(self, name):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdSelect.format(self.path, name), "")
        return content

    def BaseSelectbyIndex(self, index):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdSelectbyIndex.format(self.path, index), "")
        return status, content

    def BaseSelected(self):
        # path = self.GetControlPath()
        status, content = self.connection.GET(self.cmdSelected.format(self.path), "")
        return content


class Control:
    
    def Click(self, flag, controlName):
        """GTF方法：点击Button,CheckBox,RadioButton等控件"""
        return _BaseControl(flag, controlName).BaseClick()
    
    def ClickWW(self, flag, controlName):
        """GTF方法：点击-按钮弹窗窗体"""
        return _BaseControl(flag, controlName).BaseClickWW()
    
    def Close(self, flag, controlName):
        """GTF方法："""
        return _BaseControl(flag, controlName).BaseClose()
    
    def DbClick(self, flag, controlName):
        """GTF方法：双击"""
        return _BaseControl(flag, controlName).BaseDbClick()
    
    def DbLClickWW(self, flag, controlName, LineName):
        """GTF方法：双击 按钮弹窗窗体"""
        return _BaseControl(flag, controlName).BaseDbLClickWW(LineName)
    
    def RightClick(self, flag, controlName):
        """GTF方法：右键点击"""
        return _BaseControl(flag, controlName).BaseRightClick()
    
    def SetText(self, flag, controlName, text):
        """GTF方法：适用于Label,Edit,ComboBox等控件"""
        return _BaseControl(flag, controlName).BaseSetText(text)

    def SetTextWW(self, flag, controlName, text):
        """GTF方法：适用于Label,Edit,ComboBox等控件，设置文本后弹出窗体"""
        return _BaseControl(flag, controlName).BaseSetTextWW(text)

    def GetCount(self, flag, controlName):
        """GTF方法：适用于ListView控件"""
        return _BaseControl(flag, controlName).BaseGetCount()
    
    def GetText(self, flag, controlName):
        """GTF方法：获取Edit,ComboBox等控件的文本信息"""
        return _BaseControl(flag, controlName).BaseGetText()
    
    def Checked(self, flag, controlName):
        return _BaseControl(flag, controlName).BaseChecked()
    
    def Find(self, flag, controlName):
        return _BaseControl(flag, controlName).BaseFind()
    
    def Enabled(self, flag, controlName):
        return _BaseControl(flag, controlName).BaseEnabled()
    
    def Select(self, flag, controlName, name):
        """GTF方法：适用于ListView控件"""
        return _BaseControl(flag, controlName).BaseSelect(name)
    
    def SelectbyIndex(self, flag, controlName, index):
        """"GTF方法：适用于ListView控件，通过index查找"""
        return _BaseControl(flag, controlName).BaseSelectbyIndex(index)
    
    def Selected(self, flag, controlName):
        """GTF方法：判断listview控件是否选择"""
        return _BaseControl(flag, controlName).BaseSelected()




