"""
Provider for Cirrus CI's GraphQL API.
"""
from gqlmod.helpers.urllib import UrllibJsonProvider


class CirrusCiProvider(UrllibJsonProvider):
    endpoint = 'https://api.cirrus-ci.com/graphql'

    def __init__(self, token=None):
        self.token = token

    def modify_request(self, req):
        if self.token:
            req.add_header('Authorization', f"Bearer {self.token}")
