import requests
import ipfshttpclient


class Backend:

    def get_ipfs_document(self, document, address):
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
        source = client.cat(address).decode('utf-8')
        # root = document.import_source(source)
        root = document.import_source(source)
        return root

    def get_rest_document(self, address):
        url = address
        if not url.startswith('https'):
            url = 'https://' + url
            response = requests.get(url)
        root = response.json()
        return root

    def get_document(self, document, address):
        if address[0] == 'Q':
            return self.get_ipfs_document(document, address)
        else:
            return self.get_rest_document(address)
