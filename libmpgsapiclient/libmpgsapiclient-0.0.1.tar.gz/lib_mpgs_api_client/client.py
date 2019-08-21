from .const import host

from lib_api_client.client import PaymentClient
from lib_api_client.utils import send_third_party_request
from lib_api_client.session_pool import SessionPool

from urlparse import urljoin
from requests.auth import HTTPBasicAuth
import uuid
import json


class MPGSClient(PaymentClient):

    def __init__(self, merchant_id, api_password, channel_name='MPGS', timeout=20):
        super(MPGSClient, self).__init__(channel_name, timeout)
        self.session_pool = SessionPool(
            third_party_urls=[host]
        )
        self.merchant_id = merchant_id
        self.auth = HTTPBasicAuth('merchant.{}'.format(merchant_id), api_password)

    def _request(self, path, method, data):
        endpoint = urljoin(host, path)
        return send_third_party_request(
            endpoint,
            data,
            method=method,
            channel_name=self.channel_name,
            is_request_json=True,
            auth=self.auth,
            request_session=self.session_pool,
        )


    ##############################
    #
    # 3DS APIs
    #
    ##############################
    def check_3ds_enrollment(self, _3ds_secure_id, callback, session_id, amount, currency):
        path = 'api/rest/version/52/merchant/{}/3DSecureId/{}'.format(self.merchant_id, _3ds_secure_id)
        method = 'PUT'
        data = {
            'apiOperation': 'CHECK_3DS_ENROLLMENT',
            '3DSecure': {
                'authenticationRedirect': {
                    'responseUrl': callback
                },
            },
            'order': {
                'amount': amount,
                'currency': currency,
            },
            'session': {
                'id': session_id,
            }
        }
        return self._request(path, method, data)

    def process_acs_result(self, _3ds_secure_id, payment_authentication_response):
        path = 'api/rest/version/52/merchant/{}/3DSecureId/{}'.format(self.merchant_id, _3ds_secure_id)
        method = 'POST'
        data = {
            'apiOperation': 'PROCESS_ACS_RESULT',
            '3DSecure': {
                'paRes': payment_authentication_response
            },
        }
        return self._request(path, method, data)

    def retrive_3ds_result(self, _3ds_secure_id):
        path = 'api/rest/version/52/merchant/{}/3DSecureId/{}'.format(self.merchant_id, _3ds_secure_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    ##############################
    #
    # Session APIs
    #
    ##############################

    def create_session(self):
        path = 'api/rest/version/52/merchant/{}/session'.format(self.merchant_id)
        method = 'POST'
        data = {}
        return self._request(path, method, data)

    def retrive_session(self, session_id):
        path = 'api/rest/version/52/merchant/{}/session/{}'.format(self.merchant_id, session_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def update_session(self, session_id, card_number, expiry_month, expiry_year, security_code):
        path = 'api/rest/version/52/merchant/{}/session/{}'.format(self.merchant_id, session_id)
        method = 'PUT'
        data = {
            'sourceOfFunds': {
                'type': 'CARD',
                'provided': {
                    'card': {
                        'number': card_number,
                        'securityCode': security_code,
                        'expiry': {
                            'month': expiry_month,
                            'year': expiry_year,
                        }
                    }
                }
            }
        }
        return self._request(path, method, data)

    ##############################
    #
    # Tokenization APIs
    #
    ##############################

    def create_token(self, session_id):
        path = 'api/rest/version/52/merchant/{}/token'.format(self.merchant_id)
        method = 'POST'
        data = {
            'session': {
                'id': session_id,
            }
        }
        return self._request(path, method, data)

    def update_token(self):
        pass

    def delete_token(self, token):
        path = 'api/rest/version/52/merchant/{}/token/{}'.format(self.merchant_id, token)
        method = 'DELETE'
        data = {}
        return self._request(path, method, data)

    def retrive_token(self, session_id, token):
        path = 'api/rest/version/52/merchant/{}/token/{}'.format(self.merchant_id, token)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def search_tokens(self, card_number):
        path = 'api/rest/version/52/merchant/{}/tokenSearch'.format(self.merchant_id)
        method = 'GET'
        data = {
            'query': json.dumps({"EQ":["sourceOfFunds.provided.card.number", str(card_number)]})
        }
        return self._request(path, method, data)

    ##############################
    #
    # Transaction APIs
    #
    ##############################

    def authorize(self, session_id, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/52/merchant/{}/order/{}/transaction/{}'.format(self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'AUTHORIZE',
            'order': {
                'currency': currency,
                'amount': amount,
            },
            'session': {
                'id': session_id,
            },
        }
        return self._request(path, method, data)

    def inquiry_balance(self):
        pass

    def capture(self, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/52/merchant/{}/order/{}/transaction/{}'.format(self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'CAPTURE',
            'transaction': {
                'currency': currency,
                'amount': amount,
            },
        }
        return self._request(path, method, data)

    def pay(self, session_id, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/52/merchant/{}/order/{}/transaction/{}'.format(self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'PAY',
            'order': {
                'currency': currency,
                'amount': amount,
            },
            'session': {
                'id': session_id,
            },
        }
        return self._request(path, method, data)

    def referral(self):
        pass

    def refund(self, order_id, transaction_id, amount, currency):
        path = 'api/rest/version/52/merchant/{}/order/{}/transaction/{}'.format(self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'REFUND',
            'transaction': {
                'currency': currency,
                'amount': amount,
            },
        }
        return self._request(path, method, data)

    def retrive_order(self, order_id):
        path = 'api/rest/version/52/merchant/{}/order/{}'.format(self.merchant_id, order_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def retrive_transaction(self, order_id, transaction_id):
        path = 'api/rest/version/52/merchant/{}/order/{}/transaction/{}'.format(self.merchant_id, order_id, transaction_id)
        method = 'GET'
        data = {}
        return self._request(path, method, data)

    def update_authorization(self):
        pass

    def verify(self):
        pass

    def void(self, order_id, transaction_id, target_transaction_id):
        path = 'api/rest/version/52/merchant/{}/order/{}/transaction/{}'.format(self.merchant_id, order_id, transaction_id)
        method = 'PUT'
        data = {
            'apiOperation': 'VOID',
            'transaction': {
                'targetTransactionId': target_transaction_id,
            },
        }
        return self._request(path, method, data)
