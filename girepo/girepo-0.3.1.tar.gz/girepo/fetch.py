#!/usr/bin/env python

import requests
from datetime import datetime

BASE_URL = "https://api.github.com"


def fetch_at(full_name: str):
    full_url = "{base_url}/repos/{full_name}".format(base_url=BASE_URL, full_name=full_name)
    return fetch(full_url)


def fetch(url: str):
    with requests.get(url) as response:
        json = response.json()
        if response.status_code is not 200:
            json['status_code'] = response.status_code
            timestamp = int(response.headers['X-RateLimit-Reset'])
            json['X-RateLimit-Reset'] = datetime.fromtimestamp(timestamp).isoformat()
        return response.status_code, json


def search(repo_name: str):
    query = "?q={repo_name}&order=desc".format(repo_name=repo_name)
    full_url = "{base_url}/search/repositories{query}".format(base_url=BASE_URL, query=query)
    return fetch(full_url)
