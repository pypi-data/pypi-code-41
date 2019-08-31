"""
NeurodataLab LLC 12.04.2019
Created by Andrey Belyaev
"""
import os
import os.path as osp

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

    @staticmethod
    def create_credentials(api_keys_folder, api_url='emotionsdemo.com', api_port='50051', out_path='results'):
        # Initialize paths
        cert_home = api_keys_folder

        # Find certificate files
        cert_files = os.listdir(cert_home)
        client_crt_file, client_key_file, ca_crt_file, root_json_filepath = [''] * 4
        try:
            client_key_file = list(filter(lambda p: p.startswith('client') and p.endswith('.key'), cert_files))[0]
            client_crt_file = list(filter(lambda p: p.startswith('client') and p.endswith('.crt'), cert_files))[0]
            ca_crt_file = list(filter(lambda p: p.startswith('ca') and p.endswith('.crt'), cert_files))[0]
            root_json_filepath = list(filter(lambda p: p.startswith('root') and p.endswith('json'), cert_files))[0]
        except IndexError:
            print("You don't have all certificate's files. "
                  "Please check for client_*.key, client_*.crt, ca_*.crt, root_*.json")
            exit(0)

        # Create common auth credentials
        ssl_auth_info = SslCredential(osp.join(cert_home, client_key_file),
                                      osp.join(cert_home, client_crt_file),
                                      osp.join(cert_home, ca_crt_file))
        auth = AuthCredential('%s:%s' % (api_url, api_port), osp.join(cert_home, root_json_filepath), ssl_auth_info)

        # Create directory to store results
        if not osp.exists(out_path):
            os.mkdir(out_path)

        return auth


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
