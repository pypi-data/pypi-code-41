import requests

class BaseFactory:

    base_url = "http://localhost"
    path = "/"
    session = None
    verify_ssl = True

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def api_get_request(self, **kwargs):

        path = kwargs.get("path", self.path)
        params = kwargs.get("params", {})

        url = f"{self.base_url}{path}"

        resp = requests.get(url, params=params, verify=self.verify_ssl)

        return resp.json()
