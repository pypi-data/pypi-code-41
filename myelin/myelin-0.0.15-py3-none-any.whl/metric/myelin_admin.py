import collections
import os

import requests

ModelMetadata = collections.namedtuple('ModelMetadata', 'name model_path timestamp')


class MyelinAdminClient:
    def __init__(self):
        self.admin_url = os.environ["ADMIN_URL"]
        self.jwt_token = os.environ["ADMIN_JWT_TOKEN"]

    def get_model_backend(self, axon, model_graph, model, model_backend, namespace):
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
                                return ModelMetadata(name=model_backend, model_path=model_path,
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
