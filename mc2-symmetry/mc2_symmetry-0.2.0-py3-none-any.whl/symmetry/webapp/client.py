import json
from typing import List

import requests

from symmetry.api import NodeInfo, RoutingRecord


class NoSuchNodeException(Exception):
    pass


class NoSuchServiceException(Exception):
    pass


class ApiClient:
    api = 'http://localhost:5000/api'

    # TODO proper error handling

    # TODO better return values for actions

    def get_nodes(self) -> List[NodeInfo]:
        resp = requests.get(self._url('/nodes'))
        docs = resp.json()

        result = list()

        for doc in docs:
            if 'state' in doc:
                del doc['state']
            result.append(NodeInfo(**doc))

        return result

    def add_node(self, node):
        doc = json.dumps(node._asdict())
        requests.post(self._url('/nodes'), data=doc)

    def remove_node(self, node) -> bool:
        response = requests.delete(self._url(f'/nodes/{node}'))
        if response.status_code == 404:
            raise NoSuchNodeException(node)

        return response.ok

    def get_routes(self) -> List[RoutingRecord]:
        resp = requests.get(self._url('/routes'))
        docs = resp.json()
        return [RoutingRecord(**doc) for doc in docs]

    def get_route(self, service) -> RoutingRecord:
        resp = requests.get(self._url(f'/routes/{service}'))
        if resp.status_code == 404:
            raise NoSuchServiceException()

        doc = resp.json()
        return RoutingRecord(**doc)

    def set_route(self, record: RoutingRecord):
        doc = json.dumps(record._asdict())
        requests.post(self._url('/routes'), data=doc)

    def remove_route(self, service):
        response = requests.delete(self._url(f'/routes/{service}'))
        return response.ok

    def _url(self, path):
        return self.api + path


client = ApiClient()
