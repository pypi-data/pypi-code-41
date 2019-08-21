from Exchangesetting.dcpsetting import dcexchange
from Exchangesetting.urlinfosetting import urlinfo
from Exchangetools.dctools import getAPIkey
import requests
from Exchangesetting.gpvarsetting import gpvarsetting
from Exchangetools.dctools import exchangetopandasdf
import  json
import time
from urllib.parse import quote


class huobipro():

    def __init__(self,api_key=gpvarsetting.gpvarsettingdata['AccessKeyId'],secret_key=gpvarsetting.gpvarsettingdata[ 'SecretKey']):
        #api
        self.AccessKeyId=api_key
        self.secret_key=secret_key


    # api验证需要sort
    def apiKeySecretnoneerror(self):
        if self.AccessKeyId == None or self.AccessKeyId == '' or self.secret_key == None or self.secret_key == '':
            raise ValueError('api-key or secret_key 为空值，请输入值！  ')

    # 获取所有交易对：
    # 此接口返回所有火币全球站支持的交易对
    @staticmethod
    def getAllsymbols(exchangedata=None):
        huobi_allsymbols=requests.get(dcexchange.huobi_apiurl_setting['getAllsymbols'],headers=urlinfo.headers).json()
        if exchangedata =='data':
            return exchangetopandasdf().exchangetopandasdf(huobi_allsymbols['data'])

        # print(huobi_allsymbols)
        return huobi_allsymbols

    # 获取所有币种：
    # 此接口返回所有火币全球站支持的币种
    @staticmethod
    def getAllcurrency(exchangedata=None):
        huobi_allcurrencys=requests.get(dcexchange.huobi_apiurl_setting['getAllcurrency'],headers=urlinfo.headers).json()
        if exchangedata =='data':
            return exchangetopandasdf().exchangetopandasdf(huobi_allcurrencys['data'])
        # print(huobi_allcurrencys)
        return huobi_allcurrencys

    # 获取当前系统时间：
    # 此接口返回当前的系统时间，时间是调整为北京时间的时间戳，单位毫秒。
    @staticmethod
    def getTimestamp(exchangedata=None):
        huobi_timestamp =requests.get(dcexchange.huobi_apiurl_setting['getTimestamp'],headers=urlinfo.headers).json()
        if exchangedata =='data':
            return huobi_timestamp['data']
        # print(huobi_timestamp)
        return huobi_timestamp

    # K 线数据（蜡烛图）：
    # 此接口返回历史K线数据。
    #参数详解：period是每根蜡烛的时间区间（1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year）
           # symbol是交易对(btcusdt)，size是 K 线数据条数，可以不加此参数，默认150
    @staticmethod
    def getKline(period,symbol,size=r'150',exchangedata=None):
        huobi_kline_url=dcexchange.huobi_apiurl_setting['getVarkline'] % (period,size)+symbol
        huobi_kline=requests.get(huobi_kline_url,headers=urlinfo.headers).json()
        if exchangedata =='data':
            return exchangetopandasdf().exchangetopandasdf(huobi_kline['data'])
        return  huobi_kline

    # 聚合行情（Ticker）
    # 此接口获取ticker信息同时提供最近24小时的交易聚合信息
    #参数详解：symbol是交易对(btcusdt)
    @staticmethod
    def getTicker(symbol,exchangedata=None):
        huobi_ticker_url=dcexchange.huobi_apiurl_setting['getTicker']+symbol
        huobi_ticker=requests.get(huobi_ticker_url,headers=urlinfo.headers).json()
        if exchangedata =='data':
            orginalkeys=[]
            orginalkeys.append(huobi_ticker['tick'])
            return exchangetopandasdf().exchangetopandasdf(orginalkeys)
        # print( huobi_ticker)
        return  huobi_ticker

    # 所有交易对的最新 Tickers
    # 获得所有交易对的 tickers，数据取值时间区间为24小时滚动。
    @staticmethod
    def getAllTicker(exchangedata=None):
        huobi_allticker = requests.get(dcexchange.huobi_apiurl_setting['getAllTicker'],headers=urlinfo.headers).json()
        if exchangedata =='data':
            return exchangetopandasdf().exchangetopandasdf(huobi_allticker['data'])
        # print(huobi_allticker)
        return huobi_allticker

    # 市场深度数据
    # 此接口返回指定交易对的当前市场深度数据。
    # 参数详解：symbol是交易对(btcusdt),type是深度的价格聚合度（step0，step1，step2，step3，step4，step5），depth是返回深度的数量,默认是20
    @staticmethod
    def getMarketdepth(symbol,type,depth='20',exchangedata=None):
        huobi_marketdepth_url=dcexchange.huobi_apiurl_setting['getMarketdepth'] % (type,depth)+symbol
        huobi_marketdepth=requests.get(huobi_marketdepth_url,headers=urlinfo.headers).json()
        if exchangedata =='data':
            bidslist=[huobi_marketdepth['tick']]
            askslist=[huobi_marketdepth['tick']]
            return exchangetopandasdf().exchangetopandasdf(bidslist),exchangetopandasdf().exchangetopandasdf(askslist)


        return  huobi_marketdepth

    # 最近市场成交记录
    # 此接口返回指定交易对最新的一个交易记录
    # 参数详解：symbol是交易对(btcusdt),
    @staticmethod
    def getNewtrade(symbol,exchangedata=None):
        huobi_Newtrade_url=dcexchange.huobi_apiurl_setting['getNewtrade']+symbol
        huobi_Newtrade=requests.get(huobi_Newtrade_url,headers=urlinfo.headers).json()
        if exchangedata =='data':
            return exchangetopandasdf().exchangetopandasdf(huobi_Newtrade['tick']['data'])
        # print(huobi_Newtrade)
        return  huobi_Newtrade

    # 获得近期交易记录
    # 此接口返回指定交易对近期的所有交易记录
    # 参数详解：symbol是交易对(btcusdt),
    @staticmethod
    def getAlltrade(symbol,size=1,exchangedata=None):
        huobi_alltrade_url = dcexchange.huobi_apiurl_setting['getAlltrade'] % size + symbol
        huobi_alltrade = requests.get(huobi_alltrade_url , headers=urlinfo.headers).json()
        if exchangedata =='data':
            return exchangetopandasdf().exchangetopandasdf(huobi_alltrade['data'])

        # print(huobi_alltrade)
        return huobi_alltrade

    # 最近24小时行情数据
    # 此接口返回最近24小时的行情数据汇总
    # 参数详解：symbol是交易对(btcusdt),
    @staticmethod
    def getAlldetail(symbol,exchangedata=None):
        huobi_alldetail_url=dcexchange.huobi_apiurl_setting['getAlldetail']+symbol
        huobi_alldetail_url=requests.get(huobi_alldetail_url,headers=urlinfo.headers).json()

        if exchangedata =='data':
            huobialldetaillist=[huobi_alldetail_url['tick']]
            return exchangetopandasdf().exchangetopandasdf( huobialldetaillist)


        # print(huobi_alldetail_url)
        return  huobi_alldetail_url

    # 获取用户当前手续费率(需要登陆后操作）：
    # Api用户查询交易对费率，一次限制最多查10个交易对，子用户的费率和母用户保持一致
    def getFeerate(self,symbolrate='btcusdt',exchangedata=None):
        #条件变量添加相应的参数


        self.apiKeySecretnoneerror()
        apivarlists=dcexchange.huobi_apiurl_setting['getFeeratevar'].copy()
        apivarlists[0]=apivarlists[0]+symbolrate

        #_(self, secretkey, apilists, apikeyname, apivars):
        #参数详情：self.secret_key是secret_key，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey=getAPIkey(self.AccessKeyId,self.secret_key,dcexchange.huobi_apiurl_setting['getFeerateapi'],
                                 apivarlists).getsecretkey()
        #等到一个已经带有参数的代码
        keyurl=dcexchange.huobi_apiurl_setting['getFeerate']+ keyurlsecretkey


        #返回url值
        huobi_feerate=requests.get(  keyurl,headers=urlinfo.headers).json()


        if exchangedata =='data':


            return exchangetopandasdf().exchangetopandasdf(huobi_feerate['data'])

        # print(huobi_feerate)
        return  huobi_feerate

    # 账户信息(需要登陆后操作）
    # 查询当前用户的所有账户 ID account-id 及其相关信息(需要登陆后操作）
    def getAllaccounts(self,exchangedata=None):
        self.apiKeySecretnoneerror()
        #_(self, secretkey,  apikeyname, apivars):
        #参数详情：self.secret_key是secret_key，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey=getAPIkey(self.AccessKeyId,self.secret_key, dcexchange.huobi_apiurl_setting['getAllaccountsapi'],
                                   dcexchange.huobi_apiurl_setting['getAllaccountvar']).getsecretkey()

        #等到一个已经带有参数的代码
        keyurl=dcexchange.huobi_apiurl_setting['getAllaccounts'].copy()+ keyurlsecretkey

        #返回url值
        huobi_allaccounts=requests.get(  keyurl,headers=urlinfo.headers).json()
        if exchangedata == 'data':
            huobialldetaillist = huobi_allaccounts['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        # print(huobi_allaccounts)
        return  huobi_allaccounts

    # 账户余额(需要登陆后操作）
    # 查询指定账户的余额，支持以下账户：spot：现货账户， margin：杠杆账户，otc：OTC 账户，point：点卡账户
    def getAccountsBalance(self,accountid='9538734',exchangedata=None):
        self.apiKeySecretnoneerror()
        #条件变量添加相应的参数
        apivarlists = dcexchange.huobi_apiurl_setting['getAccountsBalancevar'].copy()
        apivarlists[0] = apivarlists[0] + accountid
        getAccountsBalance = dcexchange.huobi_apiurl_setting['getAccountsBalance'].format(accountid)
        getAccountsBalanceapi=dcexchange.huobi_apiurl_setting['getAccountsBalanceapi'].format(accountid)

        #_(self, secretkey, apilists, apikeyname, apivars):
        #参数详情：self.secret_key是secret_key，apikeyname是get\n的参数，apivars变量条件）

        keyurlsecretkey=getAPIkey(self.AccessKeyId,self.secret_key, getAccountsBalanceapi,
                                  dcexchange.huobi_apiurl_setting['getAccountsBalancevar']).getsecretkey()

        #等到一个已经带有参数的代码
        keyurl=getAccountsBalance + keyurlsecretkey

        #返回url值
        huobi_allccountsbalance=requests.get(  keyurl,headers=urlinfo.headers).json()
        if exchangedata == 'data':
            huobialldetaillist =  huobi_allccountsbalance['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)
        # print(huobi_allccountsbalance)
        return  huobi_allccountsbalance

    # 稳定币兑换汇率((需要登陆后操作）
    # 查询稳定币兑换汇率
    def getExchangerate(self,exchangedata=None):
        self.apiKeySecretnoneerror()
        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId,self.secret_key,
                                    dcexchange.huobi_apiurl_setting['getExchangeratesapi'],
                                    dcexchange.huobi_apiurl_setting['getExchangeratevar']).getsecretkey()

        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getExchangerate'].copy() + keyurlsecretkey

        # 返回url值
        huobi_Exchangerate = requests.get(keyurl, headers=urlinfo.headers).json()
        if exchangedata == 'data':
            huobialldetaillist =  huobi_Exchangerate['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        # print(huobi_Exchangerate)
        return huobi_Exchangerate

    # 虚拟币提现(需要登陆后操作)
    # API Key 权限：提币
    def postCreateWithdraw(self, address, amount, currency, addrtag=None, fee=None,chain=None,exchangedata=None ):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        if not addrtag== None:
            keyvardic['addr-tag'] = addrtag

        if not fee == None:
            keyvardic['fee'] = fee

        if not chain== None:
            keyvardic['chain'] = chain

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key, dcexchange.huobi_apiurl_setting['postCreateWithdrawapi'],
                                    apivarlists).postsecretkey()

        keyvardic['address'] = address
        keyvardic['amount'] = amount
        keyvardic['currency'] = currency
        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['postCreateWithdraw'] + keyurlsecretkey

        huobi_createWithdraw = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson, ).json()
        if exchangedata == 'data':
            huobialldetaillist =  huobi_createWithdraw ['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)


        # print(huobi_createWithdraw)
        return huobi_createWithdraw

    #此功能暂时不开通
    def postCancelWithdraw(self, withdrawid,exchangedata=None):
        # 'Depositwithdrawvar': [],
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic']
        apivarlists = ['']

        postCancelWithdrawapi1=dcexchange.huobi_apiurl_setting['postCancelWithdrawapi1'].format(withdrawid)
        postCancelWithdraw1=dcexchange.huobi_apiurl_setting['postCancelWithdraw1'].format(withdrawid)
        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    postCancelWithdrawapi1,
                                    apivarlists).postsecretkey()

        keyvardic['withdrawid'] = withdrawid
        # keyvardic['amount'] = amount
        # keyvardic['currency'] = currency
        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl =   postCancelWithdraw1 + keyurlsecretkey
        print(keyurl)
        huobi_cancelWithdraw = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson, ).json()
        print( huobi_cancelWithdraw)
        return  huobi_cancelWithdraw

    # 充提记录(需要登陆后操作)
    # 查询充提记录
    def getDepositwithdraw(self,type='deposit',currency=None,hfrom=None,size=None,direct=None,exchangedata=None):
        self.apiKeySecretnoneerror()
        # 条件变量添加相应的参数
        apivarlists = dcexchange.huobi_apiurl_setting['getDepositwithdrawvar'].copy()
        apivarlists[0] = apivarlists[0] + type

        if not currency==None:
            apivarlists.append('currency'+currency)

        if not hfrom == None:
            apivarlists.append('from' + hfrom)

        if not size == None:
            apivarlists.append('size' + size)

        if not direct == None:
            apivarlists.append('direct' + direct)

            # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId,self.secret_key, dcexchange.huobi_apiurl_setting['getDepositwithdrawapi'],
                                    apivarlists).getsecretkey()

        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getDepositwithdraw'] + keyurlsecretkey

        # 返回url值
        huobi_depositwithdraw = requests.get(keyurl, headers=urlinfo.headers).json()
        if exchangedata == 'data':
            huobialldetaillist = huobi_depositwithdraw['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        # print(huobi_depositwithdraw)
        return huobi_depositwithdraw

    # 下单充提记录(需要登陆后操作)
    # 发送一个新订单到火币以进行撮合。
    def postOrders(self,accountid,symbol,type1,amount,price=None,source='api',exchangedata=None):
        # 'Depositwithdrawvar': ['type=','symbol=','type=','amount=',],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        if not price == None:
            keyvardic['price'] = price

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey  = getAPIkey(self.AccessKeyId,self.secret_key,  dcexchange.huobi_apiurl_setting['postOrdersapi'],
                                     apivarlists ).postsecretkey()

        keyvardic['account-id']=accountid
        keyvardic['symbol'] =symbol
        keyvardic['amount'] = amount
        keyvardic['source'] = source
        keyvardic['type'] = type1
        keyvarjson =json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['postOrders'] + keyurlsecretkey

        huobi_postOrders = requests.post(keyurl, headers=urlinfo.headers,data= keyvarjson,).json()
        if exchangedata == 'data':
            huobialldetaillist =huobi_postOrders['data']
            return huobialldetaillist
        # print(huobi_postOrders)
        return huobi_postOrders


    # 撤销订单
    # 此接口发送一个撤销订单的请求。
    def postSubmmitcancel(self, orderid,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        postSubmmitcancelapi=dcexchange.huobi_apiurl_setting['postSubmmitcancelapi'].format(orderid)
        postSubmmitcancel=dcexchange.huobi_apiurl_setting['postSubmmitcancel'].format(orderid)
        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key, postSubmmitcancelapi,
                                    apivarlists).postsecretkey()

        keyvardic['order-id'] = orderid
        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl =postSubmmitcancel+ keyurlsecretkey

        huobi_submmitcancel = requests.post(keyurl, headers=urlinfo.headers,data=keyvarjson ).json()
        if exchangedata == 'data':
            huobialldetaillist = huobi_submmitcancel['data']
            return huobialldetaillist

        # print(huobi_submmitcancel)
        return huobi_submmitcancel

    # 撤销订单（基于client order ID）(需要登陆后操作)
    # 此接口发送一个撤销订单的请求。此接口只提交取消请求，实际取消结果需要通过订单状态，撮合状态等接口来确认。
    def postsubmitCancelClientOrder(self, clientorderid,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic']
        apivarlists = ['']

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key, dcexchange.huobi_apiurl_setting[ 'postsubmitCancelClientapi'],
                                    apivarlists).postsecretkey()

        keyvardic['client-order-id'] =clientorderid
        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl =dcexchange.huobi_apiurl_setting['postsubmitCancelClientOrder']+ keyurlsecretkey

        #
        # 返回url值
        print( keyurl )
        huobi_submitCancelClientOrder = requests.post(keyurl, headers=urlinfo.headers,data=keyvarjson ).json()
        # print(huobi_submitCancelClientOrder)
        if exchangedata == 'data':
            huobialldetaillist =  huobi_submitCancelClientOrder['data']
            return huobialldetaillist

        return huobi_submitCancelClientOrder


     # 查询当前未成交订单(需要登陆后操作)
     # 查询已提交但是仍未完全成交或未被撤销的订单。
    def getOpenOrders(self, accountid,symbol,side=None,size=None,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = dcexchange.huobi_apiurl_setting['getOpenOrdersapivar'].copy()
        apivarlists[0] = apivarlists[0] + accountid
        apivarlists[1] = apivarlists[1] +symbol

        if not side ==None:
            apivarlists.append(r'side ='+side)

        if not size== None:
            apivarlists.append(r'size =' + size)

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['getOpenOrdersapi'],
                                    apivarlists).getsecretkey()
        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getOpenOrders']+ keyurlsecretkey

        # 返回url值
        huobi_OpenOrders = requests.get(keyurl, headers=urlinfo.headers).json()
        if exchangedata == 'data':
            huobialldetaillist = huobi_OpenOrders ['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)


        return huobi_OpenOrders


    # 批量撤销订单(需要登陆后操作)
    # 此接口发送批量撤销订单的请求。
    def postCancelOpenOrders(self, accountid,symbol=None,side=None,size=None,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,dcexchange.huobi_apiurl_setting['postCancelOpenOrdersapi'],
                                    apivarlists).postsecretkey()

        if not symbol==None:
            keyvardic['account-id'] = accountid
            keyvardic['symbol'] = symbol

        if not side==None:
            keyvardic['side'] = side

        if not size == None:
            keyvardic['size'] = size

        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl =dcexchange.huobi_apiurl_setting['postCancelOpenOrders']+ keyurlsecretkey

        huobi_cancelOpenOrders = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson).json()
        # print(huobi_cancelOpenOrders)
        if exchangedata == 'data':
            huobialldetaillist =  [huobi_cancelOpenOrders['data']]
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        return huobi_cancelOpenOrders

    # 批量撤销订单 (需要登陆后操作)
    # 此接口同时为多个订单（基于id）发送取消请求。
    def postBatchcancel(self, orderids,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic={'order-ids':orderids}
        apivarlists = ['']

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['postBatchcancelapi'],
                                    apivarlists).postsecretkey()

        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['postBatchcancel'] + keyurlsecretkey

        huobi_batchcancel = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson).json()
        # print(huobi_batchcancel )
        if exchangedata == 'data':
            huobialldetaillist =  [ huobi_batchcancel ['data']]
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        return huobi_batchcancel

    # 查询订单详情(需要登陆后操作)
    # 此接口返回指定订单的最新状态和详情
    def getOrdersinfo(self, orderid,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = dcexchange.huobi_apiurl_setting['getOrdersinfovar'].copy()
        apivarlists[0] = apivarlists[0] + orderid

        getOrdersinfo=dcexchange.huobi_apiurl_setting['getOrdersinfo'].format(orderid)
        getOrdersinfoapi=dcexchange.huobi_apiurl_setting['getOrdersinfoapi'].format(orderid)

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    getOrdersinfoapi,
                                    apivarlists).getsecretkey()

        # 等到一个已经带有参数的代码
        keyurl = getOrdersinfo+ keyurlsecretkey

        huobi_ordersinfo = requests.get(keyurl, headers=urlinfo.headers).json()
        # print(huobi_ordersinfo)
        if exchangedata == 'data':
            huobialldetaillist = [huobi_ordersinfo ['data']]
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        return huobi_ordersinfo

    # 查询订单详情（基于client order ID）(需要登陆后操作)
    # 此接口返回指定订单的最新状态和详情。
    def getClientOrderinfo(self, clientOrderId,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = dcexchange.huobi_apiurl_setting['getClientOrderinfovar'].copy()
        apivarlists[0] = apivarlists[0] + clientOrderId

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['getClientOrderinfoapi'],
                                    apivarlists).getsecretkey()

        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getClientOrderinfo']+ keyurlsecretkey

        huobi_clientOrderinfo = requests.get(keyurl, headers=urlinfo.headers).json()
        # print(huobi_clientOrderinfo)
        if exchangedata == 'data':
            huobialldetaillist = [ huobi_clientOrderinfo ['data']]
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)
        return huobi_clientOrderinfo

    # 成交明细(需要登陆后操作)
    # 此接口返回指定订单的成交明细
    def getMatchresults(self, orderid,exchangedata=None):
        self.apiKeySecretnoneerror()
        # 条件变量添加相应的参数
        apivarlists = dcexchange.huobi_apiurl_setting['getMatchresultsvar'].copy()
        apivarlists[0] = apivarlists[0] + orderid

        getMatchresults=dcexchange.huobi_apiurl_setting['getMatchresults'].format(orderid)
        getMatchresultsapi=dcexchange.huobi_apiurl_setting['getMatchresultsapi'].format(orderid)
        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    getMatchresultsapi,
                                    apivarlists).getsecretkey()
        # 等到一个已经带有参数的代码
        keyurl = getMatchresults+ keyurlsecretkey

        # 返回url值
        huobi_matchresults = requests.get(keyurl, headers=urlinfo.headers).json()
        # print(huobi_matchresults)
        if exchangedata == 'data':
            huobialldetaillist = huobi_matchresults['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        return huobi_matchresults

    # 搜索历史订单 (需要登陆后操作)
    # 此接口基于搜索条件查询历史订单。
    def getHistoryorders(self,symbol,states,types1=None,startdate=None,enddate=None,hfrom=None,direct=None,size=None,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = dcexchange.huobi_apiurl_setting['getHistoryordersvar'].copy()
        apivarlists[0] = apivarlists[0] + symbol
        apivarlists[1] = apivarlists[1] + states

        if not types1==None:
            apivarlists.append('types='+types1)

        if not startdate== None:
            apivarlists.append('start-date=' + startdate)

        if not enddate == None:
            apivarlists.append('end-date=' + enddate)



        if not hfrom	 == None:
            apivarlists.append('from=' + hfrom)

        if not direct == None:
            apivarlists.append('direct=' + direct)

        if not size == None:
            apivarlists.append('size=' + size)

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['getHistoryordersapi'],
                                    apivarlists).getsecretkey()

        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getHistoryorders']+ keyurlsecretkey

        huobi_historyorders = requests.get(keyurl, headers=urlinfo.headers).json()
        # print(huobi_historyorders)
        if exchangedata == 'data':
            huobialldetaillist = huobi_historyorders ['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)
        return huobi_historyorders

    # 搜索最近48小时内历史订单(需要登陆后操作)
    # 此接口基于搜索条件查询最近48小时内历史订单。
    def gethistory48hours(self, symbol=None, startdate=None, enddate=None, direct=None,
                         size=None,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = dcexchange.huobi_apiurl_setting['gethistory48hoursvar'].copy()

        if not symbol == None:
            apivarlists.append('symbol=' + symbol)

        if not startdate == None:
            apivarlists.append('start-date=' + startdate)

        if not enddate == None:
            apivarlists.append('end-date=' + enddate)



        if not direct == None:
            apivarlists.append('direct=' + direct)

        if not size == None:
            apivarlists.append('size=' + size)

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['gethistory48hoursapi'],
                                    apivarlists).getsecretkey()

       # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['gethistory48hours'] + keyurlsecretkey

        huobi_history48hours = requests.get(keyurl, headers=urlinfo.headers).json()
        # print(huobi_history48hours)
        if exchangedata == 'data':
            huobialldetaillist =  huobi_history48hours['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        return huobi_history48hours

    # 当前和历史成交(需要登陆后操作)
    # 此接口基于搜索条件查询当前和历史成交记录
    def getHMatchresults(self,symbol,types1=None,startdate=None,enddate=None,hfrom=None,direct=None,size=None,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = dcexchange.huobi_apiurl_setting['getHMatchresultsvar'].copy()
        apivarlists[0] = apivarlists[0] + symbol


        if not types1==None:
            apivarlists.append('types='+types1)

        if not startdate== None:
            apivarlists.append('start-date=' + startdate)

        if not enddate == None:
            apivarlists.append('end-date=' + enddate)

        if not hfrom	 == None:
            apivarlists.append('from=' + hfrom)

        if not direct == None:
            apivarlists.append('direct=' + direct)

        if not size == None:
            apivarlists.append('size=' + size)

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['getHMatchresultsapi'],
                                    apivarlists).getsecretkey()

        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getHMatchresults']+ keyurlsecretkey

        huobi_HMatchresults = requests.get(keyurl, headers=urlinfo.headers).json()
        # print(huobi_HMatchresults)
        if exchangedata == 'data':
            huobialldetaillist =   huobi_HMatchresults['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        return huobi_HMatchresults

    # 币币现货账户与合约账户划转(需要登陆后操作)
    # 此接口用户币币现货账户与合约账户之间的资金划转。
    # 从现货现货账户转至合约账户，类型为pro-to-futures; 从合约账户转至现货账户，类型为futures-to-pro
    # 该接口的访问频次的限制为1分钟10次。
    def postAccounttransfer(self, currency,amount,type1,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,dcexchange.huobi_apiurl_setting['postAccounttransferapi'],
                                    apivarlists).postsecretkey()

        keyvardic['currency'] = currency
        keyvardic['amount'] = amount
        keyvardic['type'] = type1

        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl =dcexchange.huobi_apiurl_setting['postAccounttransfer']+ keyurlsecretkey

        huobi_accounttransfer = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson).json()
        # print(huobi_accounttransfer)
        if exchangedata == 'data':
            huobialldetaillist =   huobi_accounttransfer ['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)

        return huobi_accounttransfer

    # 资产划转(需要登陆后操作)
    # 此接口用于现货账户与杠杆账户的资产互转从现货账户划转至杠杆账户 transfer-in，从杠杆账户划转至现货账户 transfer-out
    def postMargintransferin(self, symbol,currency,amount,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,dcexchange.huobi_apiurl_setting['postMargintransferinapi'],
                                    apivarlists).postsecretkey()

        keyvardic['currency'] = currency
        keyvardic['amount'] = amount
        keyvardic['symbol'] = symbol

        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl =dcexchange.huobi_apiurl_setting['postMargintransferin']+ keyurlsecretkey

        huobi_margintransferin = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson).json()
        # print(huobi_margintransferin )
        if exchangedata == 'data':
            huobialldetaillist =huobi_margintransferin['data']
            return huobialldetaillist

        return huobi_margintransferin

    def postMargintransferout(self, symbol,currency,amount,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']
        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,dcexchange.huobi_apiurl_setting['postMargintransferoutapi'],
                                    apivarlists).postsecretkey()

        keyvardic['currency'] = currency
        keyvardic['amount'] = amount
        keyvardic['symbol'] = symbol

        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl =dcexchange.huobi_apiurl_setting['postMargintransferout']+ keyurlsecretkey


        huobi_margintransferout = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson).json()
        # print(huobi_margintransferout )

        if exchangedata == 'data':
            huobialldetaillist =huobi_margintransferout ['data']
            return huobialldetaillist

        return huobi_margintransferout

    # 申请借贷(需要登陆后操作)
    # 此接口用于申请借贷.
    def postmarginorders(self, symbol, currency, amount,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['postmarginordersapi'],
                                    apivarlists).postsecretkey()

        keyvardic['currency'] = currency
        keyvardic['amount'] = amount
        keyvardic['symbol'] = symbol

        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['postmarginorders'] + keyurlsecretkey


        huobi_marginorders = requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson).json()

        if exchangedata == 'data':
            huobialldetaillist =huobi_marginorders  ['data']
            return huobialldetaillist

        # print(huobi_marginorders)
        return huobi_marginorders

    # 归还借贷(需要登陆后操作)
    # 此接口用于归还借贷.

    def postRepay(self, orderid,  amount,exchangedata=None):
        # 'Depositwithdrawvar': [],
        self.apiKeySecretnoneerror()
        keyvardic = gpvarsetting.gpvarsettingdata['apidic'].copy()
        apivarlists = ['']

        postRepay=dcexchange.huobi_apiurl_setting['postRepay'].format(orderid)
        postRepayapi = dcexchange.huobi_apiurl_setting['postRepayapi'].format(orderid)
        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    postRepayapi,
                                    apivarlists).postsecretkey()

        keyvardic['order-id'] = orderid
        keyvardic['amount'] = amount


        keyvarjson = json.dumps(keyvardic)

        # # 等到一个已经带有参数的代码
        keyurl = postRepay + keyurlsecretkey

        #
        # 返回url值

        huobi_Repay= requests.post(keyurl, headers=urlinfo.headers, data=keyvarjson).json()
        if exchangedata == 'data':
            huobialldetaillist =  huobi_Repay['data']
            return huobialldetaillist

        # print(huobi_Repay)
        return huobi_Repay

    # 查询借贷订单(需要登陆后操作)
    # 此接口基于指定搜索条件返回借贷订单。
    def getSearchorders(self,symbol,startdate=None,enddate=None,hfrom=None,direct=None,size=None,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = dcexchange.huobi_apiurl_setting['getSearchordersvar'].copy()
        apivarlists[0] = apivarlists[0] + symbol

        if not startdate== None:
            apivarlists.append('start-date=' + startdate)

        if not enddate == None:
            apivarlists.append('end-date=' + enddate)



        if not hfrom	 == None:
            apivarlists.append('from=' + hfrom)

        if not direct == None:
            apivarlists.append('direct=' + direct)

        if not size == None:
            apivarlists.append('size=' + size)

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['getSearchordersapi'],
                                    apivarlists).getsecretkey()
        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getSearchorders']+ keyurlsecretkey

        huobi_Searchorders = requests.get(keyurl, headers=urlinfo.headers).json()

        if exchangedata == 'data':
            huobialldetaillist =  huobi_Searchorders['data']
            return huobialldetaillist

        # print(huobi_Searchorders)
        return huobi_Searchorders

    # 借贷账户详情
        # 此接口返回借贷账户详情。
    def getMarginbalance(self,symbol=None,exchangedata=None):
        # 条件变量添加相应的参数
        self.apiKeySecretnoneerror()
        apivarlists = []

        if not symbol== None:
            apivarlists.append('symbol=' + symbol)

        # _(self, secretkey, apilists, apikeyname, apivars):
        # 参数详情：self.secret_key是secret_key， apilists就是已经知道可求的餐素列表，apikeyname是get\n的参数，apivars变量条件）
        keyurlsecretkey = getAPIkey(self.AccessKeyId, self.secret_key,
                                    dcexchange.huobi_apiurl_setting['getMarginbalanceapi'],
                                    apivarlists).getsecretkey()

        # 等到一个已经带有参数的代码
        keyurl = dcexchange.huobi_apiurl_setting['getMarginbalance']+ keyurlsecretkey

        # 返回url值
        huobi_marginbalance = requests.get(keyurl, headers=urlinfo.headers).json()
        # print(huobi_marginbalance)
        if exchangedata == 'data':
            huobialldetaillist =   huobi_marginbalance ['data']
            return exchangetopandasdf().exchangetopandasdf(huobialldetaillist)


        return huobi_marginbalance


#
# if __name__ == '__main__':
#     huobipro=huobipro()
    # 获取所有交易对：
    # # #返回的参数：里面按照api参数进行付值，如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getAllsymbols())
    # print(huobipro.getAllsymbols(exchangedata='data'))
    # #
    # # 获取所有币种：
    # #返回的参数：里面按照api参数进行付值，如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getAllsymbols())
    # print(huobipro.getAllsymbols(exchangedata='data'))
    # #
    # # # 获取当前系统时间：
    # # #返回的参数：里面按照api参数进行付值，如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getTimestamp())
    # print(huobipro.getTimestamp(exchangedata='data'))
    # #
    # # # K 线数据（蜡烛图)
    # # #数详解：period是每根蜡烛的时间区间（1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year）
    # # # symbol是交易对(btcusdt)，size是 K 线数据条数，可以不加此参数，默认150
    # # #返回的参数：里面按照api参数进行付值，如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getKline('5min','btcusdt'))
    # print(huobipro.getKline('1min', 'btcusdt',size='2000',exchangedata='data'))
    # #
    #
    # # 聚合行情（Ticker）
    # # 此接口获取ticker信息同时提供最近24小时的交易聚合信息
    # #参数详解：symbol是交易对(btcusdt)如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getTicker('btcusdt'))
    # print(huobipro.getTicker('btcusdt',exchangedata='data'))
    #
    # # 所有交易对的最新 Tickers
    # # 获得所有交易对的 tickers，数据取值时间区间为24小时滚动。
    # #参数详解：symbol是交易对(btcusdt)如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getAllTicker())
    # print(huobipro.getAllTicker(exchangedata='data'))
    #
    # # 市场深度数据
    # # 此接口返回指定交易对的当前市场深度数据。如有exchangcedata='data'则返回的是panda格式
    # # 参数详解：symbol是交易对(btcusdt),type是深度的价格聚合度（step0，step1，step2，step3，step4，step5），depth是返回深度的数量,默认是20
    # print(huobipro.getMarketdepth('xrpusdt','2'))
    # print(huobipro.getMarketdepth('xrpusdt','2',exchangedata='data'))
    #
    # # 最近市场成交记录
    # # 此接口返回指定交易对最新的一个交易记录如有exchangcedata='data'则返回的是panda格式
    # # 参数详解：symbol是交易对(btcusdt),
    # print(huobipro.getNewtrade('xrpusdt'))
    # print(huobipro.getNewtrade('xrpusdt',exchangedata='data'))
    #
    #
    #
    # # 获得近期交易记录
    # # 此接口返回指定交易对近期的所有交易记录如有exchangcedata='data'则返回的是panda格式
    # # # 参数详解：symbol是交易对(btcusdt),
    # print(huobipro.getAlltrade('xrpusdt'))
    # print(huobipro.getAlltrade('xrpusdt',exchangedata='data'))
    #
    # # 最近24小时行情数据
    # # 此接口返回最近24小时的行情数据汇总如有exchangcedata='data'则返回的是panda格式
    # # 参数详解：symbol是交易对(btcusdt),
    # print(huobipro.getAlldetail('xrpusdt'))
    # print(huobipro.getAlldetail('xrpusdt',exchangedata='data'))

    # 获取用户当前手续费率(需要登陆后操作）：
    # Api用户查询交易对费率，一次限制最多查10个交易对，子用户的费率和母用户保持一致如有exchangcedata='data'则返回的是panda格式
    # print( huobipro.getFeerate(symbolrate='xrpusdt'))
    # print(huobipro.getFeerate(symbolrate='xrpusdt',exchangedata='data'))

    # 账户信息(需要登陆后操作）
    # 查询当前用户的所有账户 ID account-id 及其相关信息(需要登陆后操作）如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getAllaccounts())
    # print(huobipro.getAllaccounts(exchangedata='data'))


    # 账户余额(需要登陆后操作）
    # 查询指定账户的余额，支持以下账户：spot：现货账户， margin：杠杆账户，otc：OTC 账户，point：点卡账户如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getAccountsBalance())
    # print(huobipro.getAccountsBalance(accountid='9547894',exchangedata='data'))

    # 稳定币兑换汇率((需要登陆后操作）
    # 查询稳定币兑换汇率如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getExchangerate())
    # print(huobipro.getExchangerate(exchangedata='data'))

    # 虚拟币提现(需要登陆后操作)
    # API Key 权限：提币则返回的如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.postCreateWithdraw(gpvarsetting.gpokex['xrpwithdraw'],'10','xrp',addrtag=gpvarsetting.gpokex['xrpbiaoqian']))
    # print(huobipro.postCreateWithdraw(gpvarsetting.gpokex['xrpwithdraw'],'10','xrp',addrtag=gpvarsetting.gpokex['xrpbiaoqian'],exchangedata='data'))

    # 充提记录(需要登陆后操作)
    # 查询充提记录如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getDepositwithdraw())
    # print(huobipro.getDepositwithdraw(exchangedata='data'))

    # 下单充提记录(需要登陆后操作)
    # 发送一个新订单到火币以进行撮合。如有exchangcedata='data'则返回的是panda格式
    # a=huobipro.postOrders('9538734','xrpusdt','buy-limit','6','0.2',exchangedata='data')
    # b=huobipro.postOrders('9538734','xrpusdt','buy-limit','6','0.2',exchangedata='data')

    # 撤销订单
    # 此接口发送一个撤销订单的请求。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.postSubmmitcancel(a))
    # print(huobipro.postSubmmitcancel(b,exchangedata='data'))

    # 查询当前未成交订单(需要登陆后操作)
    # 查询已提交但是仍未完全成交或未被撤销的订单。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getOpenOrders('9538734','xrpusdt'))
    # print(huobipro.getOpenOrders('9538734', 'xrpusdt',exchangedata='data'))

    # 批量撤销订单(需要登陆后操作)
    # 此接口发送批量撤销订单的请求。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.postCancelOpenOrders('9538734'))
    # print(huobipro.postCancelOpenOrders('9538734',exchangedata='data'))


    # 下单充提记录(需要登陆后操作)
    # 发送一个新订单到火币以进行撮合。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.postBatchcancel([a,b]))
    # print(huobipro.postBatchcancel([a, b],exchangedata='data'))


    # 查询订单详情(需要登陆后操作)
    # 此接口返回指定订单的最新状态和详情如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getOrdersinfo(a))
    # print(huobipro.getOrdersinfo(a,exchangedata='data'))


    # 成交明细(需要登陆后操作)
    # 此接口返回指定订单的成交明细如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getMatchresults(a))
    # print(huobipro.getMatchresults(b,exchangedata='data'))

    # 搜索历史订单 (需要登陆后操作)
    # 此接口基于搜索条件查询历史订单。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getHistoryorders('xrpusdt','filled'))
    # print(huobipro.getHistoryorders('xrpusdt', 'filled',exchangedata='data'))


    # 搜索最近48小时内历史订单(需要登陆后操作)
    # 此接口基于搜索条件查询最近48小时内历史订单。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.gethistory48hours())
    # print(huobipro.gethistory48hours(exchangedata='data'))


    # 当前和历史成交(需要登陆后操作)
    # 此接口基于搜索条件查询当前和历史成交记录,如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getHMatchresults('xrpusdt'))
    # print(huobipro.getHMatchresults('xrpusdt',exchangedata='data'))


    # 币币现货账户与合约账户划转(需要登陆后操作)
    # 此接口用户币币现货账户与合约账户之间的资金划转。
    # 从现货现货账户转至合约账户，类型为pro-to-futures; 从合约账户转至现货账户，类型为futures-to-pro
    # 该接口的访问频次的限制为1分钟10次。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.postAccounttransfer('xrp',10.00, 'futures-to-pro'))
    # print(huobipro.postAccounttransfer('xrp',10.00,'pro-to-futures',exchangedata='data'))

    # 资产划转(需要登陆后操作)如有exchangcedata='data'则返回的是panda格式
    # 此接口用于现货账户与杠杆账户的资产互转从现货账户划转至杠杆账户 transfer-in，从杠杆账户划转至现货账户 transfer-out
    # print(huobipro.postMargintransferout('xrpusdt','xrp','3'))
    # print(huobipro.postMargintransferout('xrpusdt', 'xrp', '3',exchangedata='data'))
    # print(huobipro.postMargintransferin('xrpusdt','xrp','3'))
    # print(huobipro.postMargintransferin('xrpusdt','xrp','3',exchangedata='data'))

    # 申请借贷(需要登陆后操作)
    # 此接口用于申请借贷.如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.postmarginorders('xrpusdt','xrp','1'))
    # print(huobipro.postmarginorders('xrpusdt', 'xrp', '1',exchangedata='data'))

    # 归还借贷(需要登陆后操作)
    # 此接口用于归还借贷.如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.postRepay('32432','122'))


    # 查询借贷订单(需要登陆后操作)
    # 此接口基于指定搜索条件返回借贷订单。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getSearchorders('xrpusdt'))
    # print(huobipro.getSearchorders('xrpusdt',exchangedata='data'))

    # 借贷账户详情
    # # 此接口返回借贷账户详情。如有exchangcedata='data'则返回的是panda格式
    # print(huobipro.getMarginbalance())
    # print(huobipro.getMarginbalance(exchangedata='data'))
    #
