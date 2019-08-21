from pandas import DataFrame as df
import pandas as pd
import os
import json


class Context:
    '''
    Context是策略可以直接访问的唯一对象\n
    策略所有的接口都通过Context对象调用\n
    Context类包括以下几类接口：\n
    1、时间接口（日期、时间等），接口格式如：stra_xxx\n
    2、数据接口（K线、财务等），接口格式如：stra_xxx\n
    3、下单接口（设置目标仓位、直接下单等），接口格式如：stra_xxx\n
    '''

    def __init__(self, id, stra, wrapper, env):
        self.__stra_info__ = stra   #策略对象，对象基类BaseStrategy.py
        self.__user_data__ = dict() #用户数据
        self.__wrapper__ = wrapper
        self.__id__ = id
        self.__bar_cache__ = dict()
        self.__tick_cache__ = dict()
        self.__sname__ = stra.name()
        self.__env__ = env

    def __dump_userdata__(self):
        folder = "./pydata/"
        if not os.path.exists(folder):
            os.makedirs(folder)

        fname = folder + self.__sname__ + ".json"
        f = open(fname, 'w')
        f.write(json.dumps(self.__user_data__))
        f.close()
        
        #self.stra_log_text("用户数据已保存：" + json.dumps(self.__user_data__))

    def on_init(self):
        '''
        初始化，一般用于系统启动的时候
        '''
        folder = "./pydata/"
        if not os.path.exists(folder):
            os.makedirs(folder)

        fname = folder + self.__sname__ + ".json"
        if os.path.exists(fname):
            f = open(fname, 'r')
            data = f.read()
            self.__user_data__ = json.loads(data)
            f.close()
            #self.stra_log_text("用户数据已读取：" + data)

        self.__stra_info__.on_init(self)

    def on_getticks(self, code, curTick, isLast):
        key = code
        if key not in self.__tick_cache__:
            self.__tick_cache__[key] = list()
        elif not isinstance(self.__tick_cache__[key], list):
            self.__tick_cache__[key] = list()

        ticks = self.__tick_cache__[key]
            
        if curTick is not None:          
            tick = dict()
            tick["time"] = curTick.action_date * 1000000000 + curTick.action_time
            tick["open"] = curTick.open
            tick["high"] = curTick.high
            tick["low"] = curTick.low
            tick["price"] = curTick.price

            #tick["upper_limit"] = curTick.upper_limit
            #tick["lower_limit"] = curTick.lower_limit

            #tick["volumn"] = curTick.volumn
            #tick["totalvol"] = curTick.total_volumn
            ticks.append(tick)

        if isLast:
            localTicks = df(ticks)
            tickTime = localTicks["time"]
            localTicks.insert(0,'ticktime', tickTime)
            localTicks = localTicks.set_index("time") 
            self.__tick_cache__[key] = localTicks

    def on_getbars(self, code, period, curBar, isLast):
        key = "%s#%s" % (code, period)
        if key not in self.__bar_cache__:
            self.__bar_cache__[key] = list()
        elif not isinstance(self.__bar_cache__[key], list):
            self.__bar_cache__[key] = list()

        bars = self.__bar_cache__[key]
            
        if curBar is not None:          
            bar = dict()
            bar["time"] = 1990*100000000 + curBar.time
            bar["open"] = curBar.open
            bar["high"] = curBar.high
            bar["low"] = curBar.low
            bar["close"] = curBar.close
            bar["volumn"] = curBar.vol
            bars.append(bar)

        if isLast:
            localBars = df(bars)
            barTime = localBars["time"]
            localBars.insert(0,'bartime', barTime)
            localBars = localBars.set_index("time") 
            self.__bar_cache__[key] = localBars


    def on_tick(self):
        self.__stra_info__.on_tick(self)      


    def on_bar(self, code, period, newBar):
        '''
        K线闭合事件响应
        @code   品种代码
        @period K线基础周期
        @times  周期倍数
        @newBar 最新K线
        '''        
        key = "%s#%s" % (code, period)

        if key not in self.__bar_cache__:
            return

        try:
            self.__bar_cache__[key].loc[newBar["bartime"]] = pd.Series(newBar)
            self.__bar_cache__[key].closed = True
        except ValueError as ve:
            print(ve)
        else:
            return



    def on_calculate(self):
        self.__stra_info__.on_calculate(self)
        self.__dump_userdata__()

    def stra_log_text(self, message):
        '''
        输出日志
        @message    消息内容\n
        '''
        self.__wrapper__.ctx_str_log_text(self.__id__, message)
        
    def stra_get_date(self):
        '''
        获取当前日期\n
        @return int，格式如20180513
        '''
        return self.__wrapper__.ctx_str_get_date()

    def stra_get_position_avgpx(self, code):
        '''
        获取当前持仓均价\n
        @code   合约代码
        @return 持仓均价
        '''
        return self.__wrapper__.ctx_str_get_position_avgpx(self.__id__, code)

    def stra_get_position_profit(self, code = ""):
        '''
        获取持仓浮动盈亏
        @code   合约代码，为None时读取全部品种的浮动盈亏
        @return 浮动盈亏
        '''
        return self.__wrapper__.ctx_str_get_position_profit(self.__id__, code)

    def stra_get_time(self):
        '''
        获取当前时间，24小时制，精确到分\n
        @return int，格式如1231
        '''
        return self.__wrapper__.ctx_str_get_time()

    def stra_get_price(self, code):
        '''
        获取最新价格，一般在获取了K线以后再获取该价格
        @return 最新价格
        '''
        return self.__wrapper__.ctx_str_get_price(code)

    def stra_get_bars(self, code, period, count, isMain = False):
        '''
        获取历史K线
        @code   合约代码
        @period K线周期，如m3/d7
        @count  要拉取的K线条数
        @isMain 是否是主K线
        '''
        key = "%s#%s" % (code, period)

        if key in self.__bar_cache__:
            #这里做一个数据长度处理
            return self.__bar_cache__[key].iloc[-count:]

        cnt =  self.__wrapper__.ctx_str_get_bars(self.__id__, code, period, count, isMain)
        if cnt == 0:
            return None

        df_bars = self.__bar_cache__[key]
        df_bars.closed = False

        return df_bars

    def stra_get_ticks(self, code, count):
        '''
        获取tick数据
        @code   合约代码
        @count  要拉取的tick数量
        '''
        cnt = self.__wrapper__.ctx_str_get_ticks(self.__id__, code, count)
        if cnt == 0:
            return None
        
        df_ticks = self.__tick_cache__[code]
        return df_ticks

    def stra_get_position(self, code = "", usertag = ""):
        '''
        读取当前仓位\n
        @code   合约/股票代码\n
        @return int，正为多仓，负为空仓
        '''
        return self.__wrapper__.ctx_str_get_position(self.__id__, code, usertag)

    def stra_set_positions(self, code, qty, usertag = ""):
        '''
        设置仓位\n
        @code   合约/股票代码\n
        @qty    目标仓位，正为多仓，负为空仓\n
        @return 设置结果TRUE/FALSE
        '''
        self.__wrapper__.ctx_str_set_position(self.__id__, code, qty, usertag)
        

    def stra_enter_long(self, code, qty, usertag = ""):
        '''
        多仓进场，如果有空仓，则平空再开多\n
        @code   品种代码\n
        @qty    数量
        '''
        self.__wrapper__.ctx_str_enter_long(self.__id__, code, qty, usertag)

    def stra_exit_long(self, code, qty, usertag = ""):
        '''
        多仓出场，如果剩余多仓不够，则全部平掉即可\n
        @code   品种代码\n
        @qty    数量
        '''
        self.__wrapper__.ctx_str_exit_long(self.__id__, code, qty, usertag)

    def stra_enter_short(self, code, qty, usertag = ""):
        '''
        空仓进场，如果有多仓，则平多再开空\n
        @code   品种代码\n
        @qty    数量
        '''
        self.__wrapper__.ctx_str_enter_short(self.__id__, code, qty, usertag)

    def stra_exit_short(self, code, qty, usertag = ""):
        '''
        空仓出场，如果剩余空仓不够，则全部平掉即可\n
        @code   品种代码\n
        @qty    数量
        '''
        self.__wrapper__.ctx_str_exit_short(self.__id__, code, qty, usertag)

    def stra_get_last_entrytime(self, code):
        '''
        获取当前持仓最后一次进场时间\n
        @code   品种代码\n
        @return 返回最后一次开仓的时间，格式如201903121047
        '''
        self.__wrapper__.ctx_str_get_last_entertime(self.__id__, code)

    def stra_get_first_entrytime(self, code):
        '''
        获取当前持仓第一次进场时间\n
        @code   品种代码\n
        @return 返回最后一次开仓的时间，格式如201903121047
        '''
        self.__wrapper__.ctx_str_get_first_entertime(self.__id__, code)


    def user_save_data(self, key, data):
        '''
        保存用户数据
        @key    数据id
        @data   数据对象，可以是dict、list，或者普通数据类型
        '''
        self.__user_data__[key] = data

    def user_load_data(self, key, defVal = None):
        '''
        读取用户数据
        @key    数据id
        @defVal 默认数据，如果找不到则返回改数据，默认为None，可以是dict、list，或者普通数据类型
        '''
        if key not in self.__user_data__:
            return defVal

        return self.__user_data__[key]

    def stra_get_detail_profit(self, code, usertag, flag = 0):
        '''
        获取指定标记的持仓的盈亏
        @code       合约代码\n
        @usertag    进场标记\n
        @flag       盈亏记号，0-浮动盈亏，1-最大浮盈，2-最大亏损（负数）
        @return     盈亏 
        '''
        return self.__wrapper__.ctx_str_get_detail_profit(self.__id__, code, usertag, flag)

    def stra_get_detail_cost(self, code, usertag):
        '''
        获取指定标记的持仓的开仓价
        @code       合约代码\n
        @usertag    进场标记\n
        @return     开仓价 
        '''
        return self.__wrapper__.ctx_str_get_detail_cost(self.__id__, code, usertag)

    def stra_get_detail_entertime(self, code, usertag):
        '''
        获取指定标记的持仓的进场时间\n
        @code       合约代码\n
        @usertag    进场标记\n
        @return     进场时间，格式如201907260932 
        '''
        return self.__wrapper__.ctx_str_get_detail_entertime(self.__id__, code, usertag)

    def stra_get_comminfo(self, code):
        '''
        获取品种详情\n
        @code   合约代码如SHFE.ag.HOT，或者品种代码如SHFE.ag\n
        @return 品种信息，结构请参考ProductMgr中的ProductInfo
        '''
        if self.__env__ is None:
            return None
        return self.__env__.getProductInfo(code)