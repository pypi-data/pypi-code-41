from threading import Thread
import requests.exceptions

from printer import Printer


"""
    defines common implementation for the threaded bot
"""
class CustomThread(Thread):
    def __init__(self, id):
        super(CustomThread, self).__init__()
        self.daemon = True
        self.id = id
        self.p = Printer(id)

    def get(self, url, **kwargs):
        return self.request("get", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("post", url,  **kwargs)

    def put(self, url, **kwargs):
        return self.request("put", url,  **kwargs)

    def request(self, method, url, **kwargs):
        while True:
            try:
                if method == "get":
                    reqs = self.s.get(url, **kwargs)
                elif method == "post":
                    reqs = self.s.post(url, **kwargs)
                else:
                    reqs = self.s.put(url, **kwargs)
                self.s.headers.update({"referer":url})
                return reqs
            except requests.exceptions.Timeout:
                self.p.error("timeout")
            except requests.exceptions.ConnectionError:
                self.p.error("connection error")