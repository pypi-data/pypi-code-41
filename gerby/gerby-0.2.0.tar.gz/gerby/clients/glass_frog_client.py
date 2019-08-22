import os

import requests

from gerby.secrets import GLASSFROG_API_TOKEN


class GlassFrogClient:
    """GlassFrogClient for interacting with GlassFrog api"""

    base_url = "https://api.glassfrog.com/api/v3"

    def __init__(self, token=GLASSFROG_API_TOKEN):
        """
        Args:
            token (str): GlassFrog api token
        Returns:
            instance of GlassFrog client
        """
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Auth-Token": token,
        }

    def assignments(self):
        return self.__get("/assignments")

    def people(self):
        return self.__get("/people")

    def roles(self):
        return self.__get("/roles")

    def circles(self):
        return self.__get("/circles")

    def policies(self):
        return self.__get("/policies")

    def __parse_response(self, r):
        if r.status_code >= 400:
            return {"error": r.json()}
        else:
            return r.json()

    def __get(self, url):
        return self.__parse_response(
            requests.get(self.base_url + url, headers=self.headers)
        )
