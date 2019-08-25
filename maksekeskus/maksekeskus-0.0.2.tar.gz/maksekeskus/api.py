import requests
import simplejson as json
from maksekeskus.errors import MaksekeskusError
from requests.auth import HTTPBasicAuth

import hashlib


class MaksekeskusAPI:

    def __init__(self, live, store_id, api_secret_key, api_publishable_key,
                 version=1, session=None, timeout=30, proxies=None):
        self.base_url = "https://api.maksekeskus.ee" if live else "https://api-test.maksekeskus.ee"
        self.store_id = store_id
        self.api_secret_key = api_secret_key
        self.api_publishable_key = api_publishable_key
        self.version = version
        self.session = session or requests.Session()
        self.timeout = timeout
        self.proxies = proxies

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        self.session.close()

    def _calculate_mac(self, data):
        return hashlib.sha512(data + self.api_secret_key).hexdigest().upper()

    def request(self, path, params=None, payload=None, method=None, use_secret_key=True):
        if payload is not None:
            method = "POST"

        if method is None:
            method = "GET"

        key = self.api_secret_key if use_secret_key else self.api_publishable_key

        r = self.session.request(
            method,
            f"{self.base_url}/v{self.version}/{path}",
            timeout=self.timeout,
            json=payload,
            proxies=self.proxies,
            params=params,
            auth=HTTPBasicAuth(
                self.store_id,
                key
            )
        )
        if r.ok:
            return json.loads(r.text, use_decimal=True)
        else:
            raise MaksekeskusError(r.text)

    def get_config(self, platform):
        import maksekeskus
        return self.request(
            "shop/configuration",
            {
                "platform": platform,
                "module": maksekeskus.__version__
            },
        )

    def get_transaction(self, transaction_id):
        return self.request(
            f"transactions/{transaction_id}"
        )

    def get_transactions(self):
        return self.request(
            "transactions",
        )

    def create_transaction(self, customer, transaction):
        return self.request(
            "transactions",
            method="POST",
            payload={
                "customer": customer.dict(),
                "transaction": transaction.dict()
            }
        )
