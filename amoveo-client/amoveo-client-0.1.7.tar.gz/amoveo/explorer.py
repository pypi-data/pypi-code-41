import requests
from urllib.parse import urljoin


class AmoveoExplorer:
    def __init__(self, host):
        self.host = host

    def get_tx(self, tx_hash):
        """
        Get tx details by tx_hash.
        :param tx_hash:
        :return:
        """
        url = urljoin(self.host, "tx")
        r = requests.get(url, params={'txid': tx_hash})
        r.raise_for_status()
        tx = r.json()['result']
        return tx

    def account_txs(self, address):
        """
        Get transactions by address.
        :param address: VEO pub key
        :return:
        """
        url = urljoin(self.host, "txlist")
        r = requests.get(url, params={'address': address})
        r.raise_for_status()
        tx = r.json()['result']
        return tx
