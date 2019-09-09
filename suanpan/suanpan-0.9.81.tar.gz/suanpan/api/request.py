# coding=utf-8
from __future__ import absolute_import, print_function

import requests
from suanpan import g


def defaultCookies():
    if not g.sid or not g.sidName:
        raise Exception("Suanpan API call Error: sid and sidName not set")
    return {g.sidName: g.sid}


def getHostUrl(path, tls=False):
    if not g.host:
        raise Exception("Suanpan API call Error: host not set")
    protocol = "https" if tls else "http"
    return "{}://{}{}".format(protocol, g.host, path)


def getApiHostUrl(appId, apiName, tls=False):
    if not g.apiHost:
        raise Exception("Suanpan API call Error: apiHost not set")
    protocol = "https" if tls else "http"
    return "{}://{}/{}/{}".format(protocol, g.apiHost, appId, apiName)


def session():
    sess = requests.Session()
    sess.cookies.update(defaultCookies())
    return sess


def request(method, url, *args, **kwargs):
    sess = session()
    func = getattr(sess, method)
    url = getHostUrl(url, tls=kwargs.pop("tls", g.useTls))
    rep = func(url, *args, **kwargs)
    rep.raise_for_status()
    return rep.json()


def get(url, *args, **kwargs):
    return request("get", url, *args, **kwargs)


def post(url, *args, **kwargs):
    return request("post", url, *args, **kwargs)


def put(url, *args, **kwargs):
    return request("put", url, *args, **kwargs)


def delete(url, *args, **kwargs):
    return request("delete", url, *args, **kwargs)


def call(appId, apiName, data, *args, **kwargs):
    url = getApiHostUrl(appId, apiName, tls=kwargs.pop("tls", g.useTls))
    return requests.post(url, json={"data": data}, *args, **kwargs)
