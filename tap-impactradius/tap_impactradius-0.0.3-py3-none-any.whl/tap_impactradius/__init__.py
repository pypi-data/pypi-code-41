#!/usr/bin/env python3

from datetime import datetime, timedelta, timezone
import os
import requests
import dateutil.parser as dateparser
import urllib.parse

import singer
from singer import utils
from requests.auth import HTTPBasicAuth

LOGGER = singer.get_logger()
SESSION = requests.Session()
REQUIRED_CONFIG_KEYS = [
    "account_sid",
    "auth_token",
    "start_date",
    "validation_window",
]

CONFIG = {}
STATE = {}
BASE_HOST = "https://api.impactradius.com"
BASE_URL = "/Mediapartners/{}/{}?StartDate={}&PageSize=100"

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def load_schema(entity):
    return utils.load_json(get_abs_path("schemas/{}.json".format(entity)))

def get_start(key):
    if key not in STATE:
        STATE[key] = CONFIG['start_date']

    return dateparser.parse(STATE[key])

def get_url(endpoint, startDate):
    return BASE_URL.format(urllib.parse.quote(CONFIG['account_sid']), endpoint, urllib.parse.quote(startDate.isoformat()))

def map_types(schema, input):
    # TODO: we always assume there is only one possible type for the input
    inputType = schema["type"][0]
    if input == None:
        return input

    if inputType == "string":
        return input
    elif inputType == "integer":
        if input == "":
            return None
        return int(input)
    elif inputType == "number":
        if input == "":
            return None
        return float(input)
    elif inputType == "object":
        output = {}
        for k,v in schema['properties'].items():
            output[k] = map_types(v, input[k])
        return output
    elif inputType == "array":
        output = []
        for idx, item in enumerate(input):
            output.append(map_types(schema['items'], item))
        return output
    else:
        return input

def sync_type(type, endpoint, replicationKey, useValidationWindow):
    schema = load_schema(type)
    singer.write_schema(type, schema, [replicationKey])

    dateFrom=get_start(type)
    if useValidationWindow:
        dateFrom = dateFrom - timedelta(days=CONFIG['validation_window'])

    nextpageuri = get_url(f"{endpoint}.json", dateFrom)

    lastRow = None

    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(CONFIG['account_sid'], CONFIG['auth_token'])

    while nextpageuri != "":
        LOGGER.info(nextpageuri)

        req = requests.Request("GET", url=f"{BASE_HOST}{nextpageuri}", headers=headers, auth=auth).prepare()
        resp = SESSION.send(req)
        resp.raise_for_status()

        json = resp.json()
        for row in json.get(endpoint):
            output = map_types(schema, row)
            lastRow = output
            singer.write_record(type, output)
        nextpageuri = json['@nextpageuri']

    if lastRow != None:
        utils.update_state(STATE, type, lastRow[replicationKey])

def do_sync():
    LOGGER.info("Starting sync")

    sync_type("invoices", "Invoices", "CreatedDate", True)
    sync_type("actions", "Actions", "CreationDate", True)
    sync_type("clicks", "Clicks", "EventDate", False)

    singer.write_state(STATE)
    LOGGER.info("Sync complete")

def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    CONFIG.update(args.config)
    STATE.update(args.state)
    do_sync()


if __name__ == "__main__":
    main()
