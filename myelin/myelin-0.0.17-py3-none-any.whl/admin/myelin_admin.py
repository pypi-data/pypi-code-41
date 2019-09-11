import json
import os
from collections import namedtuple

import requests

ModelMetadata = namedtuple('ModelMetadata', 'id name url publicUrl clusterUrl status model_path timestamp')


class MyelinAdmin:
    def __init__(self):
        self.admin_url = os.environ.get("ADMIN_URL") or None
        self.jwt_token = os.environ.get("ADMIN_JWT_TOKEN") or None

    def model_backend(self, axon, model_graph, model, model_backend, namespace, default_value=None):
        if self.admin_url is None:
            return default_value

        response = requests.post("%s/model-graphs/%s" % (self.admin_url, model_graph),
                                 json={"namespace": namespace, "axon": axon},
                                 headers={'Authorization': 'Bearer %s' % self.jwt_token})

        if response.ok:
            model_graphs_rs = response.json()
            model_graphs = sorted(model_graphs_rs['deployedModelGraphs'], key=lambda x: x['startedAtTs'], reverse=True)
            if len(model_graphs) > 0:
                latest_model_graph = model_graphs[0]
                for m in latest_model_graph['models']:
                    if m['modelName'] == model:
                        for backend in m['backends']:
                            if backend['modelBackendName'] == model_backend:
                                model_path = self.get_env(backend['env'], 'MODEL_PATH')
                                return ModelMetadata(
                                    id=backend['name'],
                                    url=backend['url'],
                                    publicUrl=backend['publicUrl'],
                                    clusterUrl=backend['clusterUrl'],
                                    status=backend['status'],
                                    name=model_backend,
                                    model_path=model_path,
                                    timestamp=backend['startedAtTs'])
            else:
                return None
        else:
            raise Exception("Failed to retrieve metadata from admin host %s, got response %s " %
                            (self.admin_url, response.content))

    @staticmethod
    def get_env(env, evn_name):
        for e in env:
            if e['name'] == evn_name:
                return e['value']
        return None


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

