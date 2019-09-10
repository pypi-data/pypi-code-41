# -*- coding: utf-8 -*-

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import requests
import json
from tpspy.base import ClientBase


class ClientAudit(ClientBase):
    def __init__(self, sys_id=None, sys_secret=None, tps_base_url=None):
        super(ClientAudit, self).__init__(sys_id=sys_id, sys_secret=sys_secret, tps_base_url=tps_base_url)

    def audit_events_upload(self, data):
        url = urljoin(self.tps_base_url, "api/v1/audit/events")

        resp = requests.post(url, data=json.dumps(dict(
            data=data
        )), headers=self.post_headers)
        return self.resp_get_json(resp)
