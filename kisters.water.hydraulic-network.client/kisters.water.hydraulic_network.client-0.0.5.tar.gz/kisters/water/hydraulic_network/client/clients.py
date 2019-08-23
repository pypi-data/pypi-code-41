from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Union

import requests

from .auth import Authentication


class Client(ABC):
    @abstractmethod
    def get(
        self, resource: Union[str, Iterable[str]], parameters: Optional[dict] = None
    ) -> Union[dict, List[dict]]:
        """Get data located at a resource"""

    @abstractmethod
    def put(self, resource: Union[str, Iterable[str]], data: Union[dict, List[dict]]):
        """Overwrite data located at a resource"""

    @abstractmethod
    def post(
        self,
        resource: Union[str, Iterable[str]],
        data: Optional[Union[dict, List[dict]]] = None,
        parameters: Optional[dict] = None,
    ):
        """Send data to a resource"""

    @abstractmethod
    def delete(self, resource: Union[str, Iterable[str]]):
        """Delete data located at a resource"""


class RESTClient(Client):
    def __init__(self, url: str, authentication: Authentication = None):
        super().__init__()
        self._url = url.rstrip("/")
        self._authentication = authentication

    @property
    def url(self):
        return self._url

    def _construct_url(self, resource: Union[str, Iterable[str]]) -> str:
        if isinstance(resource, str):
            return "/".join((self.url, resource))
        return "/".join((self.url, *resource))

    def _add_auth_header(self, headers: Optional[dict] = None):
        if self._authentication:
            headers = headers or {}
            headers["Authorization"] = "Bearer {}".format(
                self._authentication.get_access_token()
            )
        return headers

    @staticmethod
    def _verify_response(response):
        if response.status_code == 422:
            raise ValueError(response.json())
        response.raise_for_status()

    def get(
        self, resource: Union[str, Iterable[str]], parameters: Optional[dict] = None
    ) -> Union[dict, List[dict]]:
        resp = requests.get(
            self._construct_url(resource),
            params=parameters,
            headers=self._add_auth_header(),
        )
        self._verify_response(resp)
        return resp.json()

    def put(self, resource: Union[str, Iterable[str]], data: Union[dict, List[dict]]):
        resp = requests.put(
            self._construct_url(resource), json=data, headers=self._add_auth_header()
        )
        self._verify_response(resp)

    def post(
        self,
        resource: Union[str, Iterable[str]],
        data: Optional[Union[dict, List[dict]]] = None,
        parameters: Optional[dict] = None,
    ):
        resp = requests.post(
            self._construct_url(resource),
            json=data,
            params=parameters,
            headers=self._add_auth_header(),
        )
        self._verify_response(resp)

    def delete(self, resource: Union[str, Iterable[str]]):
        resp = requests.delete(
            self._construct_url(resource), headers=self._add_auth_header()
        )
        self._verify_response(resp)
