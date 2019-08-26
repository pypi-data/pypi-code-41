import configparser
import time
import unittest
import uuid

from ghost.api import TraderSpi, TraderApi
from ghost.constant import Constant
from ghost.modle import OrderState, OrderTicket, Withdrawal, OrderAction, OrderType, TradingConnectionState


class TestResult:
    account_length = 3
    account_id = "410030137266"
    account_avaible = 168432454.48

    position_symbol = "603919.SH"
    position_count = 86
    position_quantity = 8000
    position_QuantityAvailable = 8000
    position_averageprice = 16.97

    order_count = 9
    order_id = "0-_410-0301-3726-6_20-1907-19_2-6016-2201"
    order_EnteredQuantity = 1000
    order_FilledQuantity = 0
    order_state = OrderState.received

    connect_state = TradingConnectionState.connectedsim
    login_result = int(Constant.LOGIN_SUCCESS_ZERO)


class MyTraderSpi(TraderSpi):
    def __init__(self):
        self.account_provider = None
        self.order_provider = None
        self.position_provider = None
        self.user_login_field = None

        self.order_return = None
        self.order_cancel_return = None
        self.order_reject_return = None
        self.trade_return = None
        self.order_canceled_return = None

        self.error = None

        self.ts_state = False
        self.guosen_state = False

        self.socket_state = False

    def on_ts_connected(self):
        self.ts_state = True

    def on_ts_disconnected(self):
        self.ts_state = False

    def on_rsp_account(self, account_provider):
        self.account_provider = account_provider

    def on_rsp_order(self, order_provider):
        self.order_provider = order_provider

    def on_guosen_disconnected(self):
        self.guosen_state = False

    def on_guosen_connected(self):
        self.guosen_state = True

    def on_rsp_position(self, position_provider):
        self.position_provider = position_provider

    def on_rtn_order(self, order_return):
        self.order_return = order_return

    def on_rtn_order_reject(self, order_reject_return):
        self.order_reject_return = order_reject_return

    def on_rtn_order_canceled(self, order_canceled_return):
        self.order_canceled_return = order_canceled_return

    def on_rtn_trade(self, trade_return):
        self.trade_return = trade_return

    def on_rtn_error(self, error):
        self.error = error

    def on_user_login(self, user_login):
        self.user_login_field = user_login

    def fire_connect(self):
        self.socket_state = True

    def fire_disconnect(self):
        self.socket_state = False

    def on_rtn_quote(self, quotes_provider):
        pass

    def on_rsp_sub_quote(self, quote):
        pass


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.api = TraderApi()
        self.spi = MyTraderSpi()

        self.api.register_spi(self.spi)
        self.api.register_front("127.0.0.1", 6807)

        self.api.init()

    def tearDown(self):
        self.api.exit()

    def test_state(self):
        time.sleep(0.01)
        self.assertTrue(self.spi.socket_state)
        self.assertTrue(self.spi.ts_state)
        self.assertTrue(self.spi.guosen_state)

    def test_user_login(self):
        time.sleep(0.01)
        self.assertIsNotNone(self.spi.user_login_field)
        self.assertEqual(self.spi.user_login_field.env, TestResult.connect_state)
        self.assertEqual(len(self.spi.user_login_field.account_infos), TestResult.account_length)

        for account_info in self.spi.user_login_field.account_infos:
            if account_info.account_id == TestResult.account_id:
                self.assertEqual(account_info.result, TestResult.login_result)

    def test_init(self):
        self.assertTrue(self.api.gsd_client.is_connect)
        self.assertIsNotNone(self.api.gsd_client.writer)
        self.assertIsNotNone(self.api.gsd_client.reader)
        self.assertFalse(self.api.gsd_client.is_stop)
        self.assertNotEqual(self.api.gsd_client.connect_num, 0)

    def test_req_account(self):
        self.assertIsNone(self.spi.account_provider)
        self.assertEqual(self.api.req_account_provider(), 0)

        time.sleep(1)
        self.assertIsNotNone(self.spi.account_provider)
        self.assertEqual(len(self.spi.account_provider.get_accounts()), TestResult.account_length)

        account = self.spi.account_provider.get_account(TestResult.account_id)
        self.assertIsNotNone(account)
        self.assertEqual(account.available, TestResult.account_avaible)

    def test_req_order(self):
        self.assertIsNone(self.spi.order_provider)
        self.assertEqual(self.api.req_order_provider(), 0)

        time.sleep(1)

        self.assertIsNotNone(self.spi.order_provider)

        order = self.spi.order_provider.get_order(TestResult.order_id)
        self.assertIsNotNone(order)
        self.assertEqual(order.account_id, TestResult.account_id)
        self.assertEqual(order.entered_quantity, TestResult.order_EnteredQuantity)
        self.assertEqual(order.filled_quantity, TestResult.order_FilledQuantity)
        self.assertEqual(order.order_state, TestResult.order_state)

    def test_req_position(self):
        self.assertIsNone(self.spi.position_provider)
        self.assertEqual(self.api.req_position_provider(), 0)

        time.sleep(1)

        self.assertIsNotNone(self.spi.position_provider)

        position = self.spi.position_provider.get_position(TestResult.position_symbol, TestResult.account_id)
        self.assertIsNotNone(position)
        self.assertEqual(len(self.spi.position_provider.get_positons()), TestResult.position_count)
        self.assertEqual(position.quantity, TestResult.position_quantity)
        self.assertEqual(position.quantity_available, TestResult.position_QuantityAvailable)
        self.assertTrue(position.average_price >= TestResult.position_averageprice)

    # @unittest.skip("not in tradeing time")
    def test_insert_cancel_order(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        order_ticket = OrderTicket()
        order_ticket.account_id = config.get('OrderTicket', 'accountId')
        order_ticket.symbol = config.get('OrderTicket', 'symbol')
        order_ticket.action = OrderAction[config.get('OrderTicket', 'action')]
        order_ticket.limit_price = config.getfloat('OrderTicket', 'limitprice')
        order_ticket.quantity = config.getint('OrderTicket', 'quantity')
        order_ticket.type = OrderType[config.get('OrderTicket', 'type')]
        order_ticket.guid = str(uuid.uuid4())

        self.assertEqual(self.api.req_order_insert(order_ticket), 0)

        time.sleep(1)
        self.assertIsNotNone(self.spi.order_return)
        self.assertTrue(
            self.spi.order_return.state == OrderState.queued or self.spi.order_return.state == OrderState.received)

        wd = Withdrawal()
        wd.account_id = config.get('Withdrawal', 'accountId')
        wd.order_sysid = self.spi.order_return.order_sysid
        self.assertEqual(self.api.req_cancel_order(wd), 0)
        print(wd.to_ts())

        time.sleep(1)
        self.assertIsNotNone(self.spi.order_canceled_return)
