import requests

from alfa_sdk.common.base import BaseResource
from alfa_sdk import resources


class AlgorithmRelease(BaseResource):
    def __init__(self, release_id, **kwargs):
        self.id = release_id
        super().__init__(**kwargs)

    def _fetch_data(self):
        return self.session.request(
            "get", "release", "/api/Releases/getInfo/{}".format(self.id)
        )

    def _fill_data(self):
        data = self.get_data()
        self.environment_id = data.get("algorithmEnvironmentId")
        self.version = data.get("version")
        self.status = data.get("status")
        self.active = data.get("active")

    #

    def get_environment(self):
        return resources.AlgorithmEnvironment(self.environment_id, session=self.session)

    def fetch_file(self):
        url = self.session.request(
            "get", "release", "/api/Releases/download/{}".format(self.id)
        )

        res = requests.get(url, allow_redirects=True)
        return res.content

    def clone(self, new_environment_id):
        body = {"releaseId": self.id, "algorithmEnvironmentId": new_environment_id}
        return self.session.request(
            "post", "release", "/api/Releases/cloneRelease", json=body
        )

    def set_active(self):
        body = {"releaseId": self.id}
        return self.session.request(
            "post", "release", "/api/Releases/setActive", json=body
        )

    def redeploy(self):
        body = {"releaseId": self.id}
        return self.session.request(
            "post", "release", "/api/Releases/deploy", json=body
        )

