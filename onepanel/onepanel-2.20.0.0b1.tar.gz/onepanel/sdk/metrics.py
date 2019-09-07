import json
import os

from websocket import create_connection


class Metrics:
    def __init__(self, account_uid, project_uid, job_uid):
        host = os.getenv('HOST', 'cluster-0-beta.onepanel.io')

        self._endpoint = 'wss://{}/{}/projects/{}/jobs/{}/metrics/:9999'.format(host, account_uid, project_uid, job_uid)
        # self._endpoint = 'ws://localhost:9999'

        self._ws = create_connection(self._endpoint)

    def close(self):
        self._ws.close()

    def put(self, x_name, x_value, y_name, y_value):
        self._ws.send(json.dumps({
            "x_axis": x_name,
            "x_value": x_value,
            "metric": y_name,
            "value": y_value
        }))


if __name__ == "__main__":
    m = Metrics("andreyonepanel", "edge-cases", "321")
    m.put("x", 1, "y", 1)
    m.close()