import requests


class SessionPool(requests.Session):
    def __init__(self, third_party_urls=None, pool_maxsize=10):
        requests.Session.__init__(self)
        if third_party_urls:
            for third_party_url in third_party_urls:
                self.mount(third_party_url, requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize))
        else:
            self.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize))
            self.mount('http://', requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize))
