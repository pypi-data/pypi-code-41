# encodint:utf8

import requests
from contextlib import closing
import json
import sys
if sys.version_info < (3, 0):
    from urlparse import urljoin  # noqa
else:
    from urllib.parse import urljoin  # noqa

DEFAULT_HTTP_TIMEOUT = 5


def get_fullurl(baseurl, relurl):
    return urljoin(baseurl, relurl)


class _HttpRequest(object):
    def __init__(self):
        pass

    def execute(self, url, dicparams, method, **kwads):
        try:
            ret = None
            mname = method.upper()
            if mname == "POST":
                ret = requests.post(url, json=dicparams, **kwads)
            elif mname == "GET":
                ret = requests.get(url, params=dicparams, **kwads)
            if ret.status_code == 200:
                return ret.text
            else:
                print(ret.status_code, url, "---->>>http raise error!@")
        except requests.exceptions.ConnectionError as identifier:
            print("Chk update failed!1")
        return ret


class DHTTPUtil(object):

    _baseurl = ""

    @classmethod
    def set_baseurl(cls, host):
        cls._baseurl = host

    @classmethod
    def http_get(cls, relurl, dicparams, **kwads):
        resp = _HttpRequest().execute(get_fullurl(cls._baseurl, relurl),
                                      dicparams, "GET", **kwads)
        if resp:
            return json.loads(resp, encoding="utf8")

    @classmethod
    def http_post(cls, relurl, dicparams, **kwads):
        resp = _HttpRequest().execute(get_fullurl(cls._baseurl, relurl),
                                      dicparams, "POST", **kwads)
        if resp:
            return json.loads(resp, encoding="utf-8")

    @classmethod
    def download_file(cls, relurl, tarf, process_cb=None):
        with closing(requests.get(relurl, stream=True)) as r:
            fsize = int(r.headers['content-length'])
            chunk_size = 1024
            nsize = 0
            with open(tarf, "wb") as fp:
                for data in r.iter_content(chunk_size=chunk_size):
                    psize = len(data)
                    nsize += psize
                    fp.write(data)
                    if hasattr(process_cb, '__call__'):
                        process_cb(nsize, fsize)


if __name__ == "__main__":
    DHTTPUtil.http_post("/api/devcli/xlmake_chkupdate",
                        {"sign": "123!@#xlmake"})
