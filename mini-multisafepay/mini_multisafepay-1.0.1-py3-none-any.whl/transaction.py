import hashlib
from xml.sax.saxutils import escape
# from xml.parsers.expat import ExpatError
from xml.etree import ElementTree as ET
import requests
import logging

API_URL = "https://testapi.multisafepay.com/ewx/"
# API_URL = "https://localhost:8000/ewx/"

# <redirect_url>%(redirect_url)s</redirect_url>
direct_transaction_template = '''<?xml version="1.0" encoding="UTF-8"?>
<directtransaction ua="MSP">
    <merchant>
        <account>%(account)s</account>
        <site_id>%(site_id)s</site_id>
        <site_secure_code>%(site_secure_code)s</site_secure_code>
        <notification_url>%(notification_url)s</notification_url>
    </merchant>
    <customer>
        <ipaddress>%(ipaddress)s</ipaddress>
    </customer>
    <transaction>
        <id>%(transaction_id)s</id>
        <currency>%(currency)s</currency>
        <amount>%(amount)s</amount>
        <description>%(description)s</description>
        <gateway>%(gateway)s</gateway>
    </transaction>
    <gatewayinfo>
        <recurringid>%(recurringid)s</recurringid>
    </gatewayinfo>
<signature>%(signature)s</signature>
</directtransaction>
'''

transaction_template = '''<?xml version="1.0" encoding="UTF-8" ?>
<redirecttransaction ua="Example 1.0">
    <merchant>
        <account>%(account)s</account>
        <site_id>%(site_id)s</site_id>
        <site_secure_code>%(site_secure_code)s</site_secure_code>
        <notification_url>%(notification_url)s</notification_url>
        <cancel_url>%(cancel_url)s</cancel_url>
        <redirect_url>%(redirect_url)s</redirect_url>
        <close_window>false</close_window>
    </merchant>
    <customer>
        <locale>%(locale)s</locale>
        <ipaddress>%(ipaddress)s</ipaddress>
        <forwardedip></forwardedip>
        <firstname></firstname>
        <lastname></lastname>
        <address1></address1>
        <address2></address2>
        <housenumber></housenumber>
        <zipcode></zipcode>
        <city></city>
        <state></state>
        <country></country>
        <phone></phone>
        <email>%(email)s</email>
    </customer>
    <transaction>
        <id>%(transaction_id)s</id>
        <currency>%(currency)s</currency>
        <amount>%(amount)s</amount>
        <description>%(description)s</description>
        <var1></var1>
        <var2></var2>
        <var3></var3>
        <items></items>
        <manual>false</manual>
    </transaction>
    <signature>%(signature)s</signature>
</redirecttransaction>'''

status_template = '''<?xml version="1.0" encoding="UTF-8"?>
<status ua="Example 1.0">
    <merchant>
        <account>%(account)s</account>
        <site_id>%(site_id)s</site_id>
        <site_secure_code>%(site_secure_code)s</site_secure_code>
    </merchant>
    <transaction>
    <id>%(transaction_id)s</id>
    </transaction>
</status>'''


class MSPError(Exception):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return u'%s: %s' % (self.code, self.description)


def get_result(url, xml_str, result_path):
    response = requests.post(url, data=xml_str)
    response.raise_for_status()
    tree = ET.fromstring(response.text)
    result = tree.get('result')
    if result == 'ok':
        return tree.find(result_path).text
    else:
        code = tree.find('error/code').text
        description = tree.find('error/description').text
        raise MSPError(code, description)


class DirectTransaction(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        if 'api_url' not in self.kwargs:
            self.kwargs['api_url'] = API_URL
        kwargs['currency'] = 'EUR'
        self.api_url = self.kwargs['api_url']
        m = hashlib.md5()
        for k in ('amount', 'currency', 'account',
                'site_id', 'transaction_id'):
            m.update(kwargs[k].encode('utf-8'))
        for k, v in self.kwargs.items():
            if v:
                self.kwargs[k] = escape(v)
            else:
                logging.info("No value for %s", k)
        self.kwargs['signature'] = m.hexdigest()

    def start(self):
        """ Post to msp """
        xml_str = direct_transaction_template % self.kwargs
        logging.info(xml_str)
        response = requests.post(self.api_url, data=xml_str, allow_redirects=False)
        tree = ET.fromstring(response.text.encode('utf-8'))
        logging.info(ET.tostring(tree))
        result = tree.get('result')
        if result != 'ok':
            code = tree.find('error/code').text
            description = tree.find('error/description').text
            raise MSPError(code, description)

    def __repr__(self):
        return str(self.kwargs)


class Transaction(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        if 'api_url' not in self.kwargs:
            self.kwargs['api_url'] = API_URL
        if 'currency' not in self.kwargs:
            kwargs['currency'] = 'EUR'
        self.api_url = self.kwargs['api_url']
        m = hashlib.md5()
        for k in ('amount', 'currency', 'account',
                'site_id', 'transaction_id'):
            m.update(kwargs[k].encode('utf-8'))
        for k, v in self.kwargs.items():
            self.kwargs[k] = escape(v)
        self.kwargs['signature'] = m.hexdigest()

    def start(self):
        """ Post to msp, this returns the payment url """
        xml_str = transaction_template % self.kwargs
        return get_result(self.api_url, xml_str, 'transaction/payment_url')

    def __str__(self):
        return self.kwargs


def get_status(**kwargs):
    if 'api_url' not in kwargs:
        kwargs['api_url'] = API_URL
    xml_str = status_template % kwargs
    return get_result(kwargs['api_url'], xml_str, 'ewallet/status')
