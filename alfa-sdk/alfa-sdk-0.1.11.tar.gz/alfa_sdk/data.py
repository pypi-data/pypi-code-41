import requests

from alfa_sdk.common.base import BaseClient


class DataClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch_data_file(self, data_file_id):
        url = self.session.request(
            "get", "data", "/api/Storages/download/{}".format(data_file_id)
        )

        res = requests.get(url["downloadLink"], allow_redirects=True)
        return res.content

    def list_data_files(self):
        return self.session.request("get", "data", "/api/Storages/list")
