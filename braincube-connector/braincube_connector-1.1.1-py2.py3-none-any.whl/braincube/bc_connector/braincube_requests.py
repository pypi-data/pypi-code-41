#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
from datetime import datetime

import requests

from braincube.bc_connector.config_handler import get_domain

logger = logging.getLogger(__name__)


class Requester:
    def __init__(self, braincube_name, sso_token):
        self.braincube_name = braincube_name
        self.sso_token = sso_token
        self.headers = {'Content-Type': 'application/json', 'Accept': "application/json", 'IPLSSOTOKEN': sso_token}

    def request_data(self, ref, selected_variables, start_date, end_date):
        # Return the result of the request of data retrieving, construct with the params of the user
        if ref['referenceDate'] not in selected_variables:
            selected_variables.append(ref['referenceDate'])
        url = "{base_url}/{mb_id}/LF".format(base_url=self.get_api_url("braindata"),
                                             mb_id=ref['name'])
        filters = [ref['order'], start_date, end_date]
        content = {
            "order": ref['referenceDate'],
            "definitions": selected_variables,
            "context":
                {
                    "dataSource": ref['name'],
                    "filter":
                        {
                            "BETWEEN": filters
                        }
                }
        }
        self.log_request("data", url, str(content))
        start_time = datetime.now().timestamp()
        result = requests.post(url, data=json.dumps(content), headers=self.headers)
        end_time = datetime.now().timestamp()
        logger.debug("[request_data][duration: time to first byte: %s s, time to last byte: %s s]",
                     "{0:.2f}".format(result.elapsed.microseconds / 1e6),
                     "{0:.2f}".format(end_time - start_time))
        return json.loads(result.text)

    def get_references(self, mb_id):
        # Return the reference of the memorybase selected
        url = "{base_url}/mb{mb_id}/simple".format(base_url=self.get_api_url("braindata"),
                                                   mb_id=str(mb_id))
        self.log_request("reference", url)
        res = requests.get(url, headers=self.headers)
        return json.loads(res.text)

    def get_data_defs(self, mb_id):
        # Return the definitions of the variables for the selected memorybase
        url = "{base_url}/mb/{mb_id}/variables/selector".format(base_url=self.get_api_url("braincube"),
                                                                mb_id=str(mb_id))
        self.log_request("datadefs", url)
        result = requests.get(url, headers=self.headers)
        return json.loads(result.text)['items']

    def get_memorybase(self):
        # Return the memorybases available for the selected braincube
        url = "{base_url}/mb/all/selector".format(base_url=self.get_api_url("braincube"))
        self.log_request("memorybase", url)
        result = requests.get(url, headers=self.headers)
        return json.loads(result.text)['items']

    def log_request(self, type, url, content="None"):
        logger.debug("Request {type}: [url: {url}, headers: {headers}, content: {content}]".format(type=type,
                                                                                                  url=url,
                                                                                                  headers=self.headers,
                                                                                                  content=content))

    def get_api_url(self, destination):
        return "https://api.{domain}/braincube/{braincube_name}/{destination}".format(domain=get_domain(),
                                                                                      braincube_name=self.braincube_name,
                                                                                      destination=destination)
