#!/usr/bin/env python
import json
import requests


__all__ = ["SimCIMClient"]


class SimCIMClient:
    """Module to solve ising problem on server
    >>> s = SimCIMClient("1238", port=5000) # doctest: +SKIP
    >>> s.execute([1, 2], [[1, 2], [3, 4]]) # doctest: +SKIP
    16
    """

    def __init__(self, api_key, endpoint="127.0.0.1", port=80):
        self.session = requests.Session()
        self.response = self.session.post(
            "http://" + endpoint + ":" + str(port) + "/login", data={"api_key": api_key}
        )
        if not self.response:
            raise ValueError("could not establish connection: " + str(self.response))

    def execute(self, h, J):
        r = self.session.post(self.response.url, data=dict(data=json.dumps((h, J))))
        return r.text


if __name__ == "__main__":
    s = SimCIMClient("1238", port=5000)
    print(s.execute([1, 2], [[1, 2], [3, 4]]))
