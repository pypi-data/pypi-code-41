import configparser
import time
import uuid
import copy

from ghost.api import TraderSpi, TraderApi
from ghost.modle import OrderTicket, Withdrawal, OrderAction, OrderType, QuotesSubscribe


class MyTraderSpi(TraderSpi):

    def on_ts_connected(self):
        print("------onTsConnected Called!------")

    def on_ts_disconnected(self):
        print("------onTsDisconnected Called!------")

    def on_rsp_account(self, account_provider):
        print("------onRspAccount Called!-----")
        print(str(account_provider))

    def on_rsp_order(self, order_provider):
        print("------onRspOrder Called!-----")
        print(str(order_provider))

    def on_guosen_disconnected(self):
        print("------onGuosenDisConnected Called!-----")

    def on_guosen_connected(self):
        print("------onGuosenConnected Called!-----")

    def on_rsp_position(self, position_provider):
        print("------PositionProvider Called!-----")
        print(str(position_provider))

    def on_rtn_order(self, order_return):
        print("------onRtnOrder Called!-----")
        print(str(order_return))

    def on_rtn_order_reject(self, order_reject_return):
        print("------OnRtnOrderReject Called!-----")
        print(str(order_reject_return))

    def on_rtn_order_canceled(self, order_canceled_return):
        print("------OnRtnOrderCanceled Called!-----")
        print(str(order_canceled_return))

    def on_rtn_trade(self, trade_return):
        print("------OnRtnTrade Called!-----")
        print(str(trade_return))

    def on_rtn_error(self, error):
        print("------OnRtnError Called!-----")
        print(str(error))

    def on_user_login(self, user_login):
        print("------OnUserLogin Called!-----")
        print(str(user_login))

    def fire_connect(self):
        print("------fireConnect Called!------")

    def fire_disconnect(self):
        print("------fireDisconnect Called!------")

    def on_rsp_sub_quote(self, quote):
        print(str(quote))

    def on_rtn_quote(self, quotes_provider):
        print(str(quotes_provider))


def show_command():
    """
    显示菜单
    :return:None
    """
    print("1.查询资金\t 2.查询持仓\t 3.查询订单")
    print("4.插入订单\t 5.撤单\t 6.重新读取配置文件")
    print("7.批量下单\t 8.订阅实时行情\t 9.退订实时行情")
    print("10.查询订阅行情列表\t")
    print("98.显示菜单\t 99.退出")


def read_config():
    """
    读取下单用的配置文件
    :return: None
    """
    config = configparser.ConfigParser()
    config.read('config.ini')

    order_ticket.account_id = config.get('OrderTicket', 'accountId')
    order_ticket.symbol = config.get('OrderTicket', 'symbol')
    order_ticket.action = OrderAction[config.get('OrderTicket', 'action')]
    order_ticket.limit_price = config.getfloat('OrderTicket', 'limitprice')
    order_ticket.quantity = config.getint('OrderTicket', 'quantity')
    order_ticket.type = OrderType[config.get('OrderTicket', 'type')]
    order_ticket.guid = str(uuid.uuid4()).replace('-', '')

    wd.account_id = config.get('Withdrawal', 'accountId')
    wd.order_sysid = config.get('Withdrawal', 'orderSysId')


def test():
    api = TraderApi()
    spi = MyTraderSpi()

    api.register_spi(spi)
    api.register_front("127.0.0.1", 6807)

    is_success = api.init()
    if not is_success:
        print("无法连接,请检查连接地址和端口是否正确!")
        return

    while True:
        time.sleep(0.5)
        show_command()
        cmd = input("请输入要进行的操作：")

        if cmd == '1':
            api.req_account_provider()
        elif cmd == '2':
            api.req_position_provider()
        elif cmd == '3':
            api.req_order_provider()
        elif cmd == '4':
            api.req_order_insert(order_ticket)
        elif cmd == '5':
            api.req_cancel_order(wd)
        elif cmd == '6':
            read_config()
        elif cmd == '7':
            order_list = list()
            for _ in range(10):
                read_config()
                order_list.append(copy.deepcopy(order_ticket))

            api.req_batch_order(order_list)
        elif cmd == '8':
            quote = QuotesSubscribe()
            quote.add_stock_code("600519.SH")
            quote.add_stock_code("000001.SZ")
            api.req_sub_quote(quote)
        elif cmd == '9':
            quote = QuotesSubscribe()
            quote.add_stock_code("600519.SH")
            quote.add_stock_code("000001.SZ")
            api.req_un_sub_quote(quote)
        elif cmd == '10':
            api.req_sub_quote_list()
        elif cmd == '98':
            show_command()
        elif cmd == '99':
            api.exit()
            break
        else:
            print("不识别的指令")


if __name__ == '__main__':
    order_ticket = OrderTicket()
    wd = Withdrawal()
    read_config()
    test()

