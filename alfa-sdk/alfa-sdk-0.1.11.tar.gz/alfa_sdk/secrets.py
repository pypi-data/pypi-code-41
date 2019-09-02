from alfa_sdk.common.base import BaseClient


class SecretsClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_names(self):
        return self.session.request("get", "secrets", "/api/parameter")

    def get_value(self, name):
        return self.session.request("get", "secrets", "/api/parameter/{}".format(name))

    def put_value(self, name, value, *, description=None):
        body = {"value": value, "description": description}
        return self.session.request(
            "put", "secrets", "/api/parameter/{}".format(name), json=body
        )

    def delete_value(self, name):
        return self.session.request(
            "delete", "secrets", "/api/parameter/{}".format(name)
        )
