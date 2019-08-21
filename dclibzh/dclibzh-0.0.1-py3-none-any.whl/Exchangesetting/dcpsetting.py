
class dcexchange():
    # 各大平台接口网址数据初始化
    # 火币网api网页初始化设置
    huobi_apiurl_setting = {
# 基础信息
        # 获取所有交易对：
        # 此接口返回所有火币全球站支持的交易对

        'getAllsymbols': r'https://api.huobi.pro/v1/common/symbols',

        # 获取所有币种：
        # 此接口返回所有火币全球站支持的币种
        'getAllcurrency': r'https://api.huobi.pro/v1/common/currencys',

        # 获取当前系统时间：
        # 此接口返回当前的系统时间，时间是调整为北京时间的时间戳，单位毫秒。
        'getTimestamp': r'https://api.huobi.pro/v1/common/timestamp',

        # 获取用户当前手续费率(需要登陆后操作）：
        # Api用户查询交易对费率，一次限制最多查10个交易对，子用户的费率和母用户保持一致
        #'getFeeratevar'和'getFeerateapi'是api验证用
        'getFeerate': 'https://api.huobi.pro/v1/fee/fee-rate/get?',
        'getFeerateapi':'GET\napi.huobi.pro\n/v1/fee/fee-rate/get\n',
        'getFeeratevar':[r'symbols='],

 # 行情获取
        # K 线数据（蜡烛图）(备注%s代表参数）：
        # 此接口返回历史K线数据。
        'getVarkline': r'https://api.huobi.pro/market/history/kline?period=%s&size=%s&symbol=',

        # 聚合行情（Ticker）
        # 此接口获取ticker信息同时提供最近24小时的交易聚合信息
        'getTicker': r'https://api.huobi.pro/market/detail/merged?symbol=',

        # 所有交易对的最新 Tickers
        # 获得所有交易对的 tickers，数据取值时间区间为24小时滚动。
        'getAllTicker': r'https://api.huobi.pro/market/tickers',

        # 市场深度数据
        # 此接口返回指定交易对的当前市场深度数据。
        # curl "https://api.huobi.pro/market/depth?symbol=btcusdt&type=step2"
        'getMarketdepth': r'https://api.huobi.pro/market/depth?type=step%s&depth=%s&symbol=',

        # 最近市场成交记录
        # 此接口返回指定交易对最新的一个交易记录
        # curl "https://api.huobi.pro/market/trade?symbol=ethusdt"
        'getNewtrade': r'https://api.huobi.pro/market/trade?symbol=',

        # 获得近期交易记录
        # 此接口返回指定交易对近期的所有交易记录
        # curl "https://api.huobi.pro/market/history/trade?symbol=ethusdt&size=2"
        'getAlltrade': r'https://api.huobi.pro/market/history/trade?size=%s&symbol=',

        # 最近24小时行情数据
        # 此接口返回最近24小时的行情数据汇总
        # curl "https://api.huobi.pro/market/detail?symbol=ethusdt"
        'getAlldetail': 'https://api.huobi.pro/market/detail?symbol=',

 # 账户相关

        # 账户信息(需要登陆后操作）
        # 查询当前用户的所有账户 ID account-id 及其相关信息(需要登陆后操作）
        'getAllaccounts': r'https://api.huobi.pro/v1/account/accounts?',
        'getAllaccountsapi': 'GET\napi.huobi.pro\n/v1/account/accounts\n',
        'getAllaccountvar': [''],

        # 账户余额(需要登陆后操作）
        # 查询指定账户的余额，支持以下账户：spot：现货账户， margin：杠杆账户，otc：OTC 账户，point：点卡账户
        'getAccountsBalance': 'https://api.huobi.pro/v1/account/accounts/{}/balance?',
        'getAccountsBalanceapi': 'GET\napi.huobi.pro\n/v1/account/accounts/{}/balance\n',
        'getAccountsBalancevar': ['account-id='],

        # 资产划转（母子账号之间）(需要登陆后操作）
        # 母账户执行母子账号之间的划转(需要登陆后操作）
        'getSubtransfer': r'https://api.huobi.pro/v1/subuser/transfer',

        # 子账号余额（汇总）((需要登陆后操作）
        # 母账户查询其下所有子账号的各币种汇总余额
        'getSubaggreagetebalance': r'https://api.huobi.pro/v1/subuser/aggregate-balance',

        # 子账号余额((需要登陆后操作）
        # 母账户查询子账号各币种账户余额
        'getSubbalance': r'https://api.huobi.pro/v1/account/accounts/',

# 稳定币兑换(暂时不开通）
        # 稳定币兑换汇率((需要登陆后操作）
        # 查询稳定币兑换汇率
        'getExchangerate': r'https://api.huobi.pro/v1/stable_coin/exchange_rate?',
        'getExchangeratesapi': 'GET\napi.huobi.pro\n/v1/stable_coin/exchange_rate\n',
        'getExchangeratevar':[''],

        # 稳定币兑换((需要登陆后操作）
        # 稳定币兑换
        'postExchange': r'https://api.huobi.pro/v1/stable_coin/exchange',

 # 钱包（充值与提现）
        # 虚拟币提现(需要登陆后操作)
        # API Key 权限：提币
        #函数参数讲解：address	（提现地址），amount（提币数量）currency	（资产类型），
        #不必须的参数：addr-tag（虚拟币共享地址tag，适用于xrp，xem，bts，steem，eos，xmr），fee（转账手续费），chain（提 USDT-ERC20 时需要设置此参数为 "usdterc20"，其他币种提现不需要设置此参数）

        'postCreateWithdraw': r'https://api.huobi.pro/v1/dw/withdraw/api/create?',
        'postCreateWithdrawapi':'POST\napi.huobi.pro\n/v1/dw/withdraw/api/create\n',
        'postCreateWithdrawvar':['address=','amount=','currency='],


        # 取消提现(需要登陆后操作)
        # API Key 权限：提币
        'postCancelWithdraw1': 'https://api.huobi.pro/v1/dw/withdraw-virtual/{}/cancel?',
        'postCancelWithdrawapi1':'POST\napi.huobi.pro\n/v1/dw/withdraw-virtual/{}/cancel\n',
        'postCancelWithdrawvar1':['withdraw-id='],

        # 充提记录(需要登陆后操作)
        # 查询充提记录
        'getDepositwithdraw': r'https://api.huobi.pro/v1/query/deposit-withdraw?',
        'getDepositwithdrawapi': 'GET\napi.huobi.pro\n/v1/query/deposit-withdraw\n',
        'getDepositwithdrawvar': ['type=',],


# 现货 / 杠杆交易
        # 下单充提记录(需要登陆后操作)
        # 发送一个新订单到火币以进行撮合。
        'postOrders': r'https://api.huobi.pro/v1/order/orders/place?',
        'postOrdersapi': 'POST\napi.huobi.pro\n/v1/order/orders/place\n',
        'postOrdersvar1': ['accountid=','symbol=','type=','amount=',],

        # 撤销订单
        # 此接口发送一个撤销订单的请求。
        'postSubmmitcancel': 'https://api.huobi.pro/v1/order/orders/{}/submitcancel?',
        'postSubmmitcancelapi': 'POST\napi.huobi.pro\n/v1/order/orders/{}/submitcancel\n',
        'postSubmmitcancelvar': ['order-id=' ],


        # 撤销订单（基于client order ID）(需要登陆后操作)
        # 此接口发送一个撤销订单的请求。此接口只提交取消请求，实际取消结果需要通过订单状态，撮合状态等接口来确认。
        'postsubmitCancelClientOrder': 'https://api.huobi.pro/v1/order/orders/submitCancelClientOrder?',
        'postsubmitCancelClientapi': 'POST\napi.huobi.pro\n/v1/order/orders/submitCancelClientOrder\n',
        'postsubmitCancelClientvar': ['client-order-id='],

        # 查询当前未成交订单(需要登陆后操作)
        # 查询已提交但是仍未完全成交或未被撤销的订单。
        'getOpenOrders': 'https://api.huobi.pro/v1/order/openOrders?',
        'getOpenOrdersapi': 'GET\napi.huobi.pro\n/v1/order/openOrders\n',
        'getOpenOrdersapivar': ['account-id=','symbol=',],


        # 批量撤销订单(需要登陆后操作)
        # 此接口发送批量撤销订单的请求。
        #account-id和symbol必须同时存在或者不存在
        'postCancelOpenOrders': 'https://api.huobi.pro/v1/order/orders/batchCancelOpenOrders?',
        'postCancelOpenOrdersapi': 'POST\napi.huobi.pro\n/v1/order/orders/batchCancelOpenOrders\n',
        'postCancelOpenOrdersvar': ['account-id=','symbol=','side=','size='],

        # 批量撤销订单 (需要登陆后操作)
        # 此接口同时为多个订单（基于id）发送取消请求。
        #参数是列表
        'postBatchcancel': 'https://api.huobi.pro/v1/order/orders/batchcancel?',
        'postBatchcancelapi': 'POST\napi.huobi.pro\n/v1/order/orders/batchcancel\n',
        'postBatchcancelsvar': [[], ],

        # 查询订单详情(需要登陆后操作)
        # 此接口返回指定订单的最新状态和详情
        'getOrdersinfo': 'https://api.huobi.pro/v1/order/orders/{}?',
        'getOrdersinfoapi': 'GET\napi.huobi.pro\n/v1/order/orders/{}\n',
        'getOrdersinfovar': ['order-id='],

        # 查询订单详情（基于client order ID）(需要登陆后操作)
        # 此接口返回指定订单的最新状态和详情。
        'getClientOrderinfo': 'https://api.huobi.pro/v1/order/orders/getClientOrder?',
        'getClientOrderinfoapi': 'GET\napi.huobi.pro\n/v1/order/orders/getClientOrder\n',
        'getClientOrderinfovar': ['clientOrderId='],

        # 成交明细(需要登陆后操作)
        # 此接口返回指定订单的成交明细
        'getMatchresults': 'https://api.huobi.pro/v1/order/orders/{}/matchresults?',
        'getMatchresultsapi': 'GET\napi.huobi.pro\n/v1/order/orders/{}/matchresults\n',
        'getMatchresultsvar': ['order-id='],

        # 搜索历史订单 (需要登陆后操作)
        # 此接口基于搜索条件查询历史订单。
        'getHistoryorders': r'https://api.huobi.pro/v1/order/orders?',
        'getHistoryordersapi': 'GET\napi.huobi.pro\n/v1/order/orders\n',
        'getHistoryordersvar': ['symbol=','states='],

        # 搜索最近48小时内历史订单(需要登陆后操作)
        # 此接口基于搜索条件查询最近48小时内历史订单。
        'gethistory48hours': r'https://api.huobi.pro/v1/order/history?',
        'gethistory48hoursapi': 'GET\napi.huobi.pro\n/v1/order/history\n',
        'gethistory48hoursvar': [],

        # 当前和历史成交(需要登陆后操作)
        # 此接口基于搜索条件查询当前和历史成交记录
        'getHMatchresults': r'https://api.huobi.pro/v1/order/matchresults?',
        'getHMatchresultsapi': 'GET\napi.huobi.pro\n/v1/order/matchresults\n',
        'getHMatchresultsvar': ['symbol='],


        # 币币现货账户与合约账户划转(需要登陆后操作)
        # 此接口用户币币现货账户与合约账户之间的资金划转。
        # 从现货现货账户转至合约账户，类型为pro-to-futures; 从合约账户转至现货账户，类型为futures-to-pro
        # 该接口的访问频次的限制为1分钟10次。
        'postAccounttransfer': r'https://api.huobi.pro/v1/futures/transfer?',
        'postAccounttransferapi': 'POST\napi.huobi.pro\n/v1/futures/transfer\n',
        'postAccounttransfervar': ['currency=','amount=','type='],

 # 借贷
        # 资产划转(需要登陆后操作)
        # 此接口用于现货账户与杠杆账户的资产互转从现货账户划转至杠杆账户 transfer-in，从杠杆账户划转至现货账户 transfer-out
        'postMargintransferin': r'https://api.huobi.pro/v1/dw/transfer-in/margin?',
        'postMargintransferinapi': 'POST\napi.huobi.pro\n/v1/dw/transfer-in/margin\n',
        'postMargintransferinvar': ['symbol=','currency=' ,'amount=', ],

        'postMargintransferout': 'https://api.huobi.pro/v1/dw/transfer-out/margin?',
        'postMargintransferoutapi': 'POST\napi.huobi.pro\n/v1/dw/transfer-out/margin\n',
        'postMargintransferoutvar': ['symbol=', 'currency=', 'amount=', ],

        # 申请借贷(需要登陆后操作)
        # 此接口用于申请借贷.
        'postmarginorders': r'https://api.huobi.pro/v1/margin/orders?',
        'postmarginordersapi': 'POST\napi.huobi.pro\n/v1/margin/orders\n',
        'postmarginordersvar': ['symbol=', 'currency=', 'amount=', ],

        # 归还借贷(需要登陆后操作)
        # 此接口用于归还借贷.
        'postRepay': r'https://api.huobi.pro/v1/margin/orders/{}/repay?',
        'postRepayapi': 'POST\napi.huobi.pro\n/v1/margin/orders/{}/repay\n',
        'postRepayvar': ['order-id=', 'amount=', ],



        # 查询借贷订单(需要登陆后操作)
        # 此接口基于指定搜索条件返回借贷订单。
        'getSearchorders': r'https://api.huobi.pro/v1/margin/loan-orders?',
        'getSearchordersapi': 'GET\napi.huobi.pro\n/v1/margin/loan-orders\n',
        'getSearchordersvar': ['symbol=', ],
        # 借贷账户详情
        # 此接口返回借贷账户详情。
        'getMarginbalance': r'https://api.huobi.pro/v1/margin/accounts/balance?',
        'getMarginbalanceapi': 'GET\napi.huobi.pro\n/v1/margin/accounts/balance\n',
        'getMarginbalancevar': [],




    }






