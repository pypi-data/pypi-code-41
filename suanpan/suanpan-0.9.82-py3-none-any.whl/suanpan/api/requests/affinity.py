# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g
from suanpan.api import requests


def getAffinityUrl(path, tls=g.affinityTls):
    host = g.affinity or g.host
    if not g.affinity and not g.host:
        raise Exception("Suanpan API call Error: affinity and host not set")
    protocol = "https" if tls else "http"
    return "{}://{}{}".format(protocol, host, path)


def get(path, *args, **kwargs):
    return requests.request("get", getAffinityUrl(path), *args, **kwargs)


def post(path, *args, **kwargs):
    return requests.request("post", getAffinityUrl(path), *args, **kwargs)


def put(path, *args, **kwargs):
    return requests.request("put", getAffinityUrl(path), *args, **kwargs)


def delete(path, *args, **kwargs):
    return requests.request("delete", getAffinityUrl(path), *args, **kwargs)
