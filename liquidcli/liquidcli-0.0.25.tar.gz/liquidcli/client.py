import requests
import time
import jwt
from .decoder import (
    decoder_Page,
    decoder_shallowList,
    decoder_shallowObject,
)
from .data import (
    FiatAccount,
    AccountDetail,
    CryptoAccount,
    ReservedBalance,
    Execution,
    Order,
    Page,
)

BASE_URL = 'https://api.liquid.com'

DEFAULT_REQUEST_HEADERS = {
    'X-Quoine-API-Version': '2',
    'Content-Type': 'application/json',
}


class Client(object):
    def __init__(self, baseUrl: str = BASE_URL, apiTokenId: str = '', apiSecret: str = '', noncer=lambda: int(round(time.time() * 1000))):
        self.baseUrl: str = baseUrl
        self.apiTokenId: str = apiTokenId
        self.apiSecret: str = apiSecret
        self.__sess: requests.Session = requests.Session()
        self.noncer = noncer

    def __jwt(self, p: str):
        payload = {
            'nonce': self.noncer(),
            'token_id': self.apiTokenId,
            'path': p,
        }
        return jwt.encode(payload, self.apiSecret, 'HS256')

    def __requestPri(self, method: str, p: str, objectHook: object,
                     params=None, data=None, headers=None, cookies=None, files=None,
                     auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None,
                     stream=None, verify=None, cert=None, json=None):
        headers['X-Quoine-Auth'] = self.__jwt(p)
        return self.__request(
            method, p, objectHook,
            params, data, headers, cookies, files,
            auth, timeout, allow_redirects, proxies, hooks,
            stream, verify, cert, json,
        )

    def __request(self, method: str, p: str, objectHook: object,
                  params=None, data=None, headers=None, cookies=None, files=None,
                  auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None,
                  stream=None, verify=None, cert=None, json=None):
        res: requests.Response = self.__sess.request(
            method, '{0}{1}'.format(self.baseUrl, p),
            params=params, data=data, headers=headers, cookies=cookies, files=files,
            auth=auth, timeout=timeout, allow_redirects=allow_redirects,
            proxies=proxies, hooks=hooks, stream=stream,
            verify=verify, cert=cert, json=json,
        )
        res.raise_for_status()
        return res.json(object_hook=objectHook)

    def getExecutions(self, productId: int, limit: int, page: int):
        return self.__request(
            'get', '/executions',
            decoder_Page(Execution),
            params={'product_id': productId, 'limit': limit, 'page': page},
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def getExecutionsByTimestamp(self, currencyPairCode: str, timestamp: int, limit: int):
        return self.__request(
            'get', '/executions',
            decoder_shallowList(Execution),
            params={'currency_pair_code': currencyPairCode,
                    'limit': limit, 'timestamp': timestamp},
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def getFiatAccounts(self):
        return self.__requestPri(
            'get', '/fiat_accounts',
            decoder_shallowList(FiatAccount),
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def getCryptoAccounts(self):
        return self.__requestPri(
            'get', '/crypto_accounts',
            decoder_shallowList(CryptoAccount),
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def getAccountDetail(self, currency: str):
        return self.__requestPri(
            'get', '/accounts/{}'.format(currency),
            decoder_shallowObject(AccountDetail),
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def getReservedBalanceDetails(self, currency: str):
        return self.__requestPri(
            'get', '/accounts/{}/reserved_balance_details'.format(currency),
            decoder_shallowList(ReservedBalance),
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def getOrdersById(
        self,
        id: int = -1,
    ) -> Page:
        return self.__requestPri(
            'get', '/orders/{}'.format(id),
            decoder_Page(Order),
            params={},
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def getOrders(
        self,
        funding_currency: str = '',
        product_id: int = -1,
        status: str = '',
        trading_type: str = '',
        with_details: int = -1,
    ) -> Page:
        params = {}
        if funding_currency != '':
            params['funding_currency'] = funding_currency
        if product_id >= 0:
            params['product_id'] = product_id
        if status != '':
            params['status'] = status
        if trading_type != '':
            params['trading_type'] = trading_type
        if with_details >= 0:
            params['with_details'] = with_details
        return self.__requestPri(
            'get', '/orders',
            decoder_Page(Order),
            params=params,
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def postOrders(
        self,
        product_id: int,
        order_type: str,
        side: str,
        quantity: float,
        price: float = -1,
        trading_type: str = '',
        margin_type: str = '',
        price_range: str = '',
        client_order_id: str = '',
    ) -> Order:
        data = {
            'order': {
                'product_id': product_id,
                'order_type': order_type,
                'side': side,
                'quantity': quantity,
                'price': price,
            },
        }
        if trading_type != '':
            data['order']['trading_type'] = trading_type
        if margin_type != '':
            data['order']['margin_type'] = margin_type
        if price_range != '':
            data['order']['price_range'] = price_range
        if price >= 0:
            data['order']['price'] = price
        if client_order_id != '':
            data['order']['client_order_id'] = client_order_id
        return self.__requestPri(
            'post', '/orders',
            decoder_Page(Order),
            json=data,
            params={},
            headers=DEFAULT_REQUEST_HEADERS,
        )

    def cancelOrders(
        self,
        id: int,
    ) -> Order:
        return self.__requestPri(
            'put', '/orders/{0}/cancel'.format(id),
            decoder_shallowObject(Order),
            params={},
            headers=DEFAULT_REQUEST_HEADERS,
        )
