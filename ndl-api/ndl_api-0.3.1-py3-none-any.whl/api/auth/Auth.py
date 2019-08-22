"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""
import ndlapi.api.utils.ioutil as ioutil


class SslCredential:

    def __init__(self, user_key, chain, root_ca):
        self.user_key = ioutil.read_binary(user_key)
        self.user_cert = ioutil.read_binary(chain)
        self.server_ca = ioutil.read_binary(root_ca)

    def key(self):
        return self.user_key

    def cert(self):
        return self.user_cert

    def ca(self):
        return self.server_ca


class AuthCredential:

    def __init__(self, target_host, token, ssl_credentials):
        self.user_token = ioutil.read_binary(token)
        self.ssl = ssl_credentials
        self.server_host = target_host

    def token(self):
        return self.user_token.decode()

    def ssl_credentials(self):
        return self.ssl

    def host(self):
        return self.server_host
