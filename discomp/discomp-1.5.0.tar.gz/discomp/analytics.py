import json
import os
import uuid

import analytics


def setup_analytics():
    file_path = '.config'
    if analytics.write_key:
        return
    if not os.path.exists(file_path):
        mydir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(mydir, '.config')
    if not os.path.exists(file_path):
        return
    with open(file_path) as json_file:
        data = json.load(json_file)
        if not data["segment"]:
            return
        analytics.write_key = data["segment"]


def track(event, payload, user_id=str(uuid.uuid4())):
    if analytics.write_key:
        payload["interface"] = "MP"
        analytics.track(user_id, event, payload)
