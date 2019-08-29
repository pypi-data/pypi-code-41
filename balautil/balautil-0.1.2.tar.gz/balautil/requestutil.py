import requests
import logging
globalheaders = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
}

## Common HTTP Util methods

def GetRaw(url, **kwgs):
    if kwgs.get("headers"):
        headers = {**globalheaders, **kwgs.get("headers")}
    else:
        headers = globalheaders
    resp = requests.get(url, headers=headers)
    return resp

def Get(url, **kwgs):
    if kwgs.get("headers"):
        headers = {**globalheaders, **kwgs.get("headers")}
    else:
        headers = globalheaders
    resp = requests.get(url, headers=headers)
    return RespUtil.Parse(resp)

def Post(url, **kwgs):
    if kwgs.get("headers"):
        headers = {**globalheaders, **kwgs.get("headers")}
    else:
        headers = globalheaders
    resp = requests.post(url, data=kwgs.get("data"), json=kwgs.get("json"), headers=headers)
    return RespUtil.Parse(resp)

def Put(url, **kwgs):
    if kwgs.get("headers"):
        headers = {**globalheaders, **kwgs.get("headers")}
    else:
        headers = globalheaders
    resp = requests.put(url, data=kwgs.get("data"), headers=headers)
    return RespUtil.Parse(resp)

def Delete(url, **kwgs):
    if kwgs.get("headers"):
        headers = {**globalheaders, **kwgs.get("headers")}
    else:
        headers = globalheaders
    resp = requests.delete(url, headers=headers)
    return RespUtil.Parse(resp)

# Util class to parse http Response
class RespUtil:
    
    @staticmethod
    def Parse(resp):
        if resp.ok:
            try:
                r = resp.json()
            except Exception as e:
                logging.info(e)
                r = resp.text
            finally:
                return r    