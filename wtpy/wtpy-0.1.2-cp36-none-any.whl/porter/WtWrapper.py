from ctypes import cdll, c_int, c_char_p, c_longlong, c_bool, c_void_p, c_ulong, c_uint
from .WtDefine import CB_STRATEGY_INIT, CB_STRATEGY_TICK, CB_STRATEGY_CALC, CB_STRATEGY_BAR, CB_STRATEGY_GET_BAR, CB_STRATEGY_GET_TICK
from .WtStructs import WTSBarStruct
import platform
import os
import sys

theEnv = None


def isPythonX64():
    ret = platform.architecture()
    return (ret[0] == "64bit")

#回调函数
def on_strategy_init(id):
    env = theEnv
    ctx = env.get_context(id)
    if ctx is not None:
        ctx.on_init()
    return

def on_strategy_tick(id):
    env = theEnv
    ctx = env.get_context(id)
    if ctx is not None:
        ctx.on_tick()
    return

def on_strategy_calc(id):
    env = theEnv
    ctx = env.get_context(id)
    if ctx is not None:
        ctx.on_calculate()
    return

def on_strategy_bar(id, code, period, newBar):
    env = theEnv
    ctx = env.get_context(id)
    newBar = newBar.contents
    curBar = dict()
    curBar["time"] = 1990*100000000 + newBar.time
    curBar["bartime"] = curBar["time"]
    curBar["open"] = newBar.open
    curBar["high"] = newBar.high
    curBar["low"] = newBar.low
    curBar["close"] = newBar.close
    curBar["volumn"] = newBar.vol
    if ctx is not None:
        ctx.on_bar(bytes.decode(code), bytes.decode(period), curBar)
    return


def on_strategy_get_bar(id, code, period, curBar, isLast):
    env = theEnv
    ctx = env.get_context(id)
    realBar = None
    if curBar:
        realBar = curBar.contents
    if ctx is not None:
        ctx.on_getbars(bytes.decode(code), bytes.decode(period), realBar, isLast)
    return

def on_strategy_get_tick(id, code, curTick, isLast):
    env = theEnv
    ctx = env.get_context(id)
    realTick = None
    if curTick:
        realTick = curTick.contents
    if ctx is not None:
        ctx.on_getticks(bytes.decode(code), realTick, isLast)
    return

'''
将回调函数转换成C接口识别的函数类型
''' 
cb_strategy_init = CB_STRATEGY_INIT(on_strategy_init)
cb_strategy_tick = CB_STRATEGY_TICK(on_strategy_tick)
cb_strategy_calc = CB_STRATEGY_CALC(on_strategy_calc)
cb_strategy_bar = CB_STRATEGY_BAR(on_strategy_bar)
cb_strategy_get_bar = CB_STRATEGY_GET_BAR(on_strategy_get_bar)
cb_strategy_get_tick = CB_STRATEGY_GET_TICK(on_strategy_get_tick)

# Python对接C接口的库
class WtWrapper:
    '''
    Wt平台C接口底层对接模块
    '''

    # api可以作为公共变量
    api = None
    ver = "Unknown"
    
    # 构造函数，传入动态库名
    def __init__(self):
        paths = os.path.split(__file__)
        if isPythonX64():
            dllname = "./bin/X64/WtPorter.dll"
            a = (paths[:-1] + (dllname,))
            _path = os.path.join(*a)
            self.api = cdll.LoadLibrary(_path)
        else:
            dllname = "./bin/Win32/WtPorter.dll"
            a = (paths[:-1] + (dllname,))
            _path = os.path.join(*a)
            self.api = cdll.LoadLibrary(_path)
        self.api.get_version.restype = c_char_p
        self.ver = bytes.decode(self.api.get_version())

    def run(self):
        self.api.run_porter(True)

    def write_log(self, level, message, catName = ""):
        self.api.write_log(level, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'), bytes(catName, encoding = "utf8"))

    def initialize(self, env, cfgfile = 'config.json'):
        '''
        C接口初始化
        '''
        global theEnv
        theEnv = env
        try:
            self.api.init_porter(bytes(cfgfile, encoding = "utf8"), cb_strategy_init, cb_strategy_tick, cb_strategy_calc, cb_strategy_bar)
        except OSError as oe:
            print(oe)

        self.write_log(102, "Wt交易框架已初始化完成，框架版本号：%s" % (self.ver))

    def create_context(self, name):
        '''
        创建策略环境\n
        @name      策略名称
        @return    系统内策略ID 
        '''
        return self.api.create_context(bytes(name, encoding = "utf8") )

    def ctx_str_enter_long(self, id, code, qty, usertag):
        '''
        开多\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.ctx_str_enter_long(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"))

    def ctx_str_exit_long(self, id, code, qty, usertag):
        '''
        平多\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.ctx_str_exit_long(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"))

    def ctx_str_enter_short(self, id, code, qty, usertag):
        '''
        开空\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.ctx_str_enter_short(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"))

    def ctx_str_exit_short(self, id, code, qty, usertag):
        '''
        平空\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.ctx_str_exit_short(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"))

    def ctx_str_get_bars(self, id, code, period, count, isMain):
        '''
        读取K线\n
        @id     策略id\n
        @code   合约代码\n
        @period 周期，如m1/m3/d1等\n
        @count  条数\n
        @isMain 是否主K线
        '''
        return self.api.ctx_str_get_bars(id, bytes(code, encoding = "utf8"), bytes(period, encoding = "utf8"), count, isMain, cb_strategy_get_bar)

    def ctx_str_get_ticks(self, id, code, count):
        '''
        读取Tick\n
        @id     策略id\n
        @code   合约代码\n
        @count  条数\n
        '''
        return self.api.ctx_str_get_ticks(id, bytes(code, encoding = "utf8"), count, cb_strategy_get_tick)

    def ctx_str_get_position_profit(self, id, code):
        '''
        获取浮动盈亏\n
        @id     策略id\n
        @code   合约代码\n
        @return 指定合约的浮动盈亏
        '''
        return self.api.ctx_str_get_position_profit(id, bytes(code, encoding = "utf8"))

    def ctx_str_get_position_avgpx(self, id, code):
        '''
        获取持仓均价\n
        @id     策略id\n
        @code   合约代码\n
        @return 指定合约的持仓均价
        '''
        return self.api.ctx_str_get_position_avgpx(id, bytes(code, encoding = "utf8"))
    
    def ctx_str_get_position(self, id, code, usertag = ""):
        '''
        获取持仓\n
        @id     策略id\n
        @code   合约代码\n
        @usertag    进场标记，如果为空则获取该合约全部持仓\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.ctx_str_get_position(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8"))

    def ctx_str_get_price(self, code):
        '''
        @code   合约代码\n
        @return 指定合约的最新价格 
        '''
        return self.api.ctx_str_get_price(bytes(code, encoding = "utf8"))

    def ctx_str_set_position(self, id, code, qty, usertag):
        '''
        设置目标仓位\n
        @id     策略id
        @code   合约代码\n
        @qty    目标仓位，正为多，负为空
        '''
        self.api.ctx_str_set_position(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"))

    def ctx_str_get_date(self):
        '''
        获取当前日期\n
        @return    当前日期 
        '''
        self.api.ctx_str_get_date()

    def ctx_str_get_time(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        self.api.ctx_str_get_time()

    def ctx_str_get_first_entertime(self, code):
        '''
        获取当前持仓的首次进场时间\n
        @code       合约代码\n
        @return     进场时间，格式如201907260932 
        '''
        self.api.ctx_str_get_first_entertime(bytes(code, encoding = "utf8"))

    def ctx_str_get_last_entertime(self, code):
        '''
        获取当前持仓的最后进场时间\n
        @code       合约代码\n
        @return     进场时间，格式如201907260932 
        '''
        self.api.ctx_str_get_last_entertime(bytes(code, encoding = "utf8"))

    def ctx_str_log_text(self, id, message):
        '''
        日志输出\n
        @id         策略ID\n
        @message    日志内容
        '''
        self.api.ctx_str_log_text(id, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'))

    def ctx_str_get_detail_entertime(self, id, code, usertag):
        '''
        获取指定标记的持仓的进场时间\n
        @id         策略id\n
        @code       合约代码\n
        @usertag    进场标记\n
        @return     进场时间，格式如201907260932 
        '''
        self.api.ctx_str_get_detail_entertime(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8")) 

    def ctx_str_get_detail_cost(self, id, code, usertag):
        '''
        获取指定标记的持仓的开仓价
        @id         策略id\n
        @code       合约代码\n
        @usertag    进场标记\n
        @return     开仓价 
        '''
        self.api.ctx_str_get_detail_cost(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8")) 

    def ctx_str_get_detail_profit(self, id, code, usertag, flag):
        '''
        获取指定标记的持仓的盈亏
        @id         策略id\n
        @code       合约代码\n
        @usertag    进场标记\n
        @flag       盈亏记号，0-浮动盈亏，1-最大浮盈，2-最大亏损（负数）
        @return     盈亏 
        '''
        self.api.ctx_str_get_detail_profit(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8"), flag) 
  
