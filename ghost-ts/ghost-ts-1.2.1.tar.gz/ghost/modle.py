import datetime
import os
from enum import Enum, unique

from ghost.constant import Constant


class QuotesSubscribe(object):
    """
    行情：订阅--退订
    """

    def __init__(self, args=""):
        self.codes = set()

        if len(args) > 0:
            value_split = args.split(Constant.FIELD_SEP)
            [self.codes.add(code) for code in value_split]

    def add_stock_code(self, code):
        """
        增加股票代码
        :param code:  股票代码
        :return: true代表增加成功
        """
        if len(code) != 9:
            return False

        self.codes.add(code)
        return True

    def remove_stock_code(self, code):
        """
        删除股票代码
        :param code: 股票代码
        :return: None
        """
        self.codes.remove(code)

    def to_ts(self):
        """
        转换为发送到TS的字符串
        :return: 字符串连接对象
        """
        return Constant.FIELD_SEP.join(self.codes)

    def __str__(self):
        return self.to_ts()


class QuotesProvider(object):
    """
    实时行情提供对象
    """

    def __init__(self, args):
        value_split = args.split(Constant.FIELD_SEP)
        if len(value_split) == 17:
            index = 0
            self.symbol = value_split[index]
            index += 1
            self.ask = float(value_split[index])
            index += 1
            self.ask_size = int(value_split[index])
            index += 1
            self.bid = float(value_split[index])
            index += 1

            self.bid_size = int(value_split[index])
            index += 1

            self.daily_close = float(value_split[index])
            index += 1

            self.daily_high = float(value_split[index])
            index += 1

            self.daily_low = float(value_split[index])
            index += 1

            self.daily_open = float(value_split[index])
            index += 1

            self.daily_volume = int(value_split[index])
            index += 1

            self.last = float(value_split[index])
            index += 1

            self.trade_date = value_split[index]
            index += 1

            self.trade_time = value_split[index]
            index += 1

            self.trade_volume = int(value_split[index])
            index += 1

            self.high_limit = float(value_split[index])
            index += 1

            self.low_limit = float(value_split[index])
            index += 1

            self.description = value_split[index]

    def __str__(self):
        return str.format("股票代码：{0} 股票名称：{1} 最新价：{2} 行情事件：{3}", self.symbol, self.description, self.last,
                          self.trade_time)


class ErrorInfo:
    def __init__(self, args):
        if len(args) == 2:
            self.error_message = args[0]
            self.error_context = args[1]
            self.error_time = datetime.datetime.now()
        else:
            raise TypeError("只能有两个参数")

    def __str__(self):
        return str.format("时间:{0}   消息:{1}  上下文:{2}", self.error_time, self.error_message, self.error_context)


@unique
class TradingConnectionState(Enum):
    """
    交易连接环境
    """
    #  实盘
    connectedlive = 2
    #  模拟
    connectedsim = 3
    #  未连接
    disconnected = 1
    #  不可用
    notenabled = 4
    #  未知
    unknown = 0


class UserLoginField(object):
    """
    用户登录结果
    """

    def __init__(self, args):
        value_split = args.split(Constant.FIELD_SEP)

        if len(value_split) != 2:
            raise ValueError("UserLoginField args length is not 2")

        index = 0
        self.env = TradingConnectionState[value_split[index]]
        index += 1

        self.account_infos = []
        s_account_info = value_split[index]
        if len(s_account_info) > 0:
            if s_account_info.endswith(Constant.LINE_SEP):
                s_account_info = s_account_info[:-1]

            account_info_list = s_account_info.split(Constant.LINE_SEP)
            for account_info in account_info_list:
                self.account_infos.append(AccountInfo(account_info.split(Constant.AND_SEP)))

    def __str__(self):
        return str.format("连接环境：{0}\n", self.env) + os.linesep.join(
            [str(account_login) for account_login in self.account_infos])


class AccountInfo(object):
    """
    账户登录结果
    """

    def __init__(self, args):
        if len(args) != 5:
            raise ValueError("AccountLogin args length is not 5")

        index = 0
        self.account_id = args[index]
        index += 1
        self.account_type = AccountType[args[index]]
        index += 1
        self.account_state = AccountState[args[index]]
        index += 1
        self.result = int(args[index])
        index += 1
        self.message = args[index]

    def __str__(self):
        return str.format("账户ID：{0} 账户类型：{1} 账户状态：{2} 登录结果：{3} 登录消息：{4}", self.account_id, self.account_type,
                          self.account_state, self.result, self.message)


@unique
class AccountType(Enum):
    """
    账户类型
    """
    #  现金账户
    cash = 1
    #  期货账户
    futures = 5
    #  无效账户
    invalid = 0
    #  受限账户
    limitedmargin = 8
    #  保证金账户
    margin = 2
    #  期权账户
    option = 9


class AccountState(Enum):
    """
    账户状态
    """
    #  初始化完成
    initialized = 2
    #  正在初始化
    initializing = 1
    #  初始化失败
    uninitialized = 0


class Account:
    """
    账户信息对象：包含了资金的信息
    account_id：账号ID
    available：可用资金
    balance：总资产
    market_value：市值
    """

    def __init__(self, value):
        if len(value) != 4:
            raise ValueError("length is not 4")
        self.account_id = value[0]
        self.available = float(value[1])
        self.balance = float(value[2])
        self.market_value = float(value[3])

    def __str__(self):
        return str.format("账户ID:{0}   可用资金:{1}  总资产:{2}  市值:{3}", self.account_id, self.available, self.balance,
                          self.market_value)


class AccountsProvider:
    """
    账户对象集合：包含了所有的账户信息
    """

    def __init__(self, args):
        if not isinstance(args, str):
            raise TypeError("must be str")
        else:
            self.__accounts = []
            if len(args) > 0:
                if args.endswith(Constant.LINE_SEP):
                    args = args[:-1]
                account_list = args.split(Constant.LINE_SEP)

                for account_string in account_list:
                    self.__accounts.append(Account(account_string.split(Constant.FIELD_SEP)))
            else:
                self.__accounts = []

    def get_accounts(self):
        """
        获取账户对象集合
        :return: list 账户对象
        """
        return self.__accounts

    def get_account(self, account_id):
        """
        获取指定的账户对象
        :param account_id: 账户ID
        :return: 账户对象
        """
        for account in self.__accounts:
            if account.account_id == account_id:
                return account

        return None

    def __str__(self):
        return os.linesep.join([str(account) for account in self.__accounts])


class BasicOrderReturn:
    def __init__(self, symbol, order_guid, order_sysid):
        self.symbol = symbol
        self.order_guid = order_guid
        self.order_sysid = order_sysid

    def __str__(self):
        return str.format("股票代码:{0}   用户唯一标识符:{1}  柜台唯一标识符:{2}", self.symbol, self.order_guid, self.order_sysid)


#  订单类型
@unique
class OrderType(Enum):
    """
    订单类型
    """
    #  限价单
    limit = 1
    #  市价单
    market = 2
    #  限价止损单
    stoplimit = 3
    #  市价止损单
    stopmarket = 4
    #  未知
    unknown = 0


class Order:
    """
    订单对象
    """

    def __init__(self, ls, index):
        self.account_id = ls[index]
        index += 1
        self.action = OrderAction[ls[index]]
        index += 1
        self.average_price = float(ls[index])
        index += 1
        self.entered_quantity = int(ls[index])
        index += 1
        self.entered_time = ls[index]
        index += 1
        self.filled_quantity = int(ls[index])
        index += 1
        self.filled_time = ls[index]
        index += 1
        self.left_quantity = int(ls[index])
        index += 1
        self.limit_price = float(ls[index])
        index += 1
        self.order_id = ls[index]
        index += 1
        self.order_state = OrderState[ls[index]]
        index += 1
        self.symbol = ls[index]
        index += 1
        self.order_type = OrderType[ls[index]]
        index += 1
        self.guid = ls[index]

    def __str__(self):
        return str.format("账户ID:{0}   订单方向:{1}  平均成交价:{2}", self.symbol, self.action, self.average_price)


@unique
class OrderAction(Enum):
    #  借款买入股票
    borrowtobuy = 11
    #  卖出股票以支付债务
    borrowtosell = 14
    #  买入
    buy = 1
    #  买入平仓
    buytoclose = 19
    #  买入补仓
    buytocover = 4
    #  买入开仓
    buytoopen = 17
    #  买入股票以支付股票债务
    buytopay = 13
    #  买入担保品
    collateralbuy = 15
    #  卖出担保品
    collateralsell = 16
    #  补空平仓
    covertoclose = 22
    #  补空开仓
    covertoopen = 21
    #  购买 etf
    etfpurchase = 31
    #  赎回 etf
    etfredeem = 33
    #  行使期权
    exerciseoption = 34
    #  合并结构型基金
    merge = 27
    #  支付货币债务
    paybycash = 26
    #  支付股票债务
    paybystock = 25
    #  购买可交易基金
    purchase = 29
    #  赎回可交易基金
    redeem = 30
    #  卖出股票
    sell = 2
    #  卖空
    sellshort = 3
    #  卖出平仓
    selltoclose = 18
    #  卖出开仓
    selltoopen = 20
    #  卖出股票以支付债务
    selltopay = 12
    #  拆分结构型基金
    split = 28
    #  未知
    unknown = 0
    #  锁定证券
    unlock = 36
    #  解锁证券
    Lock = 35


#  订单状态
@unique
class OrderState(Enum):
    #  订单撤销过期
    cancelpending = 10
    #  订单被取消
    canceled = 9
    #  订单过期
    expired = 12
    #  订单全部成交
    filled = 8
    #  订单部分成交
    partiallyfilled = 6
    #  订单部分成交，剩余撤销
    partiallyfilledurout = 7
    #  订单再队列中
    queued = 5
    #  柜台收到订单
    received = 4
    #  订单被拒绝
    rejected = 11
    #  订单发送失败
    sendfailed = 3
    #  订单正在被发送
    sending = 1
    #  发送订单
    sent = 2
    #  订单未发送
    unsent = 0


class OrderUpdateReason(Enum):
    # 订单增加
    added = 0
    # 订单初始化
    initialupdate = 3
    # 订单被删除
    removed = 1
    # 订单状态发生变化
    statechanged = 2


class OrderUpdatedEventArgs(object):
    def __init__(self, args):
        if not isinstance(args, str):
            raise TypeError("must be str")

        args = args.split(Constant.FIELD_SEP)

        index = 0
        self.accountId = args[index]
        index += 1
        self.message = args[index]
        index += 1
        self.order_id = args[index]
        index += 1
        self.symbol = args[index]
        index += 1
        self.state = OrderState[args[index]]
        index += 1
        self.reason = OrderUpdateReason[args[index]]
        index += 1
        self.order = Order(args, index)


class OrderCanceledReturn(BasicOrderReturn):
    def __init__(self, args):
        BasicOrderReturn.__init__(self, args.symbol, args.order.guid, args.order_id)
        self.filled_quantity = args.order.filled_quantity

    def __str__(self):
        return super().__str__() + str.format(" 成交数量：{0}", self.filled_quantity)


class OrdersProvider:
    def __init__(self, args):
        if not isinstance(args, str):
            raise TypeError("must be str ")
        else:
            self.__orders = []
            if len(args) > 0:
                if args.endswith(Constant.LINE_SEP):
                    args = args[:-1]
                order_list = args.split(Constant.LINE_SEP)

                for order_String in order_list:
                    self.__orders.append(Order(order_String.split(Constant.FIELD_SEP), 0))
            else:
                self.__orders = []

    def get_orders(self):
        return self.__orders

    def get_order(self, order_id):
        for order in self.__orders:
            if order.order_id == order_id:
                return order

        return None

    def __str__(self):
        return os.linesep.join([str(order) for order in self.__orders])


class OrderRejectReturn(BasicOrderReturn):
    def __init__(self, args):
        BasicOrderReturn.__init__(self, args.symbol, args.order.guid, args.order_id)
        self.status_msg = args.message

    def __str__(self):
        return super().__str__() + str.format(" 被拒绝消息：{0}", self.status_msg)


class OrderReturn(BasicOrderReturn):
    def __init__(self, args):
        if not isinstance(args, OrderUpdatedEventArgs):
            raise TypeError("args must be set to an OrderUpdatedEventArgs")

        BasicOrderReturn.__init__(self, args.symbol, args.order.guid, args.order_id)
        self.filled_quantity = args.order.filled_quantity
        self.balance_traded = args.order.average_price * self.filled_quantity
        self.state = args.state

    def __str__(self):
        return super().__str__() + str.format(" 成交数量：{0} 成交金额：{1} 订单状态：{2}", self.filled_quantity, self.balance_traded,
                                              self.state)


class OrderTicket:
    """
    下单对象
    """

    def __init__(self):
        self.symbol = ""
        self.account_id = ""
        self.limit_price = 0
        self.action = None
        self.quantity = 0
        self.type = None
        self.guid = ""

    def to_ts(self):
        return Constant.FIELD_SEP.join(
            [self.symbol, self.account_id, str(self.limit_price), str(self.action.value), str(self.quantity),
             str(self.type.value), self.guid])


class TradeReturn(BasicOrderReturn):
    def __init__(self, args):
        if not isinstance(args, OrderUpdatedEventArgs):
            raise TypeError("args must be set to an OrderUpdatedEventArgs")

        BasicOrderReturn.__init__(self, args.symbol, args.order.guid, args.order_id)
        self.volume = args.order.filled_quantity
        self.price = args.order.average_price
        self.trade_balance = self.volume * self.price
        self.trade_time = args.order.filled_time

    def __str__(self):
        return super().__str__() + str.format(" 总成交量：{0} 平均成交价：{1} 总成交金额：{2} 成交时间：{3}", self.volume, self.trade_balance,
                                              self.trade_time)


class Withdrawal:
    """
    撤单对象
    account_id：账户ID
    order_sysid：柜台唯一标识符
    """

    def __init__(self):
        self.account_id = ""
        self.order_sysid = ""

    def to_ts(self):
        return Constant.FIELD_SEP.join([self.account_id, self.order_sysid])


class Position:
    """
    仓位对象
    """

    def __init__(self, ls):
        if len(ls) != 8:
            raise ValueError("length is not 8")

        index = 0
        self.account_id = ls[index]
        index += 1
        self.symbol = ls[index]
        index += 1
        self.average_price = float(ls[index])
        index += 1
        self.quantity = int(ls[index])
        index += 1
        self.openpl = float(ls[index])
        index += 1
        self.market_value = float(ls[index])
        index += 1
        self.quantity_available = int(ls[index])
        index += 1
        self.position_id = ls[index]

    def __str__(self):
        return str.format("账户ID：{0} 股票代码：{1} 平均成交价：{2} 所有数量：{3}", self.account_id, self.symbol, self.average_price,
                          self.quantity)


class PositionsProvider:
    """
    仓位对象集合
    """

    def __init__(self, args):
        if not isinstance(args, str):
            raise TypeError("must be str")
        else:
            self.__positions = []
            if len(args) > 0:
                if args.endswith(Constant.LINE_SEP):
                    args = args[:-1]
                position_list = args.split(Constant.LINE_SEP)

                for position_string in position_list:
                    self.__positions.append(Position(position_string.split(Constant.FIELD_SEP)))
            else:
                self.__positions = []

    def get_positons(self):
        return self.__positions

    def get_position(self, symbol, account_id):
        for position in self.__positions:
            if position.symbol == symbol and position.account_id == account_id:
                return position

        return None

    def __str__(self):
        return os.linesep.join([str(position) for position in self.__positions])
