#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import json

logger = logging.getLogger("uaa_client")
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class UAAClient(object):
    def __init__(self, client, username: str="", password: str="", entrypoint: str="", job_access_token: str=None):
        self.client = client
        self.username = username
        self.password = password
        self.entrypoint = entrypoint
        self.job_access_token = job_access_token
        self.headers = {
            "Content-Type": "application/json"
        }

    def set_token(self, token):
        self.job_access_token = token

    def get_token(self):
        if self.job_access_token:
            return self.job_access_token
            
        status_code, response = self.client.post(self.entrypoint, headers=self.headers, json={
            'username': self.username,
            'password': self.password
        })
        logger.info("get token %s: [%d]", self.entrypoint, status_code)
        if status_code == 200:
            data = json.loads(response.content)
            return data['token']
        else:
            logger.info(response)
            return None


