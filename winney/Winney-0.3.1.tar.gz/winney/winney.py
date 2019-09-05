#coding:utf-8
import json
# import redis
import chardet
import requests
import urllib.parse
from requests.utils import guess_json_utf

# CACHE just for get 

# META_CACHE_KEY    = "WINNEY:META:{REQUEST_URL}"
# CONTENT_CACHE_KEY = "WINNEY:CONTENT:{REQUEST_URL}"

# red = redis.Redis(host="localhost")

class Result(object):
    """
    cache_time 废弃，不再缓存结果
    redis_conn 废弃，不再缓存结果
    """
    def __init__(self, resp=None, url=None, method=None, cache_time=None, redis_conn=None):
        if resp and not isinstance(resp, requests.Response):
            raise Exception("resp should be object of requests.Response, but {} found.".format(type(resp)))
        self.status   = resp.ok
        self.reason   = resp.reason
        self.content  = resp.content
        self.headers  = resp.headers.__repr__()
        self.encoding = resp.encoding
        # self.redis_conn = redis_conn
        self.status_code = resp.status_code
        self.request_url = url
        self.request_method = method
        self.encoding = None
        # if not self.encoding:
        #     self.encoding = chardet.detect(self.content)["encoding"]
        # self.set_cache(cache_time)
    
    # def set_cache(self, cache_time):
    #     if not (self.redis_conn and cache_time):
    #         return
    #     if not (self.request_method and self.request_method.upper() == "GET"):
    #         print("Cache just for GET, but {} found".format(self.request_method))
    #         return None
    #     meta_data = {
    #         "status":self.status,
    #         "reason":self.reason,
    #         "headers":self.headers,
    #         "encoding":self.encoding,
    #         "status_code":self.status_code,
    #         "request_url":self.request_url,
    #     }
    #     meta_key    = META_CACHE_KEY.format(REQUEST_URL=self.request_url)
    #     content_key = CONTENT_CACHE_KEY.format(REQUEST_URL=self.request_url)
    #     self.redis_conn.set(meta_key, json.dumps(meta_data), ex=cache_time)
    #     self.redis_conn.set(content_key, self.content, ex=cache_time)
    
    # @classmethod
    # def load_from_cache(cls, request_url, request_method, redis_conn):
    #     if not (redis_conn and request_method and request_method.upper() == "GET"):
    #         print("Cache not found.")
    #         return None
    #     meta_key    = META_CACHE_KEY.format(REQUEST_URL=request_url)
    #     content_key = CONTENT_CACHE_KEY.format(REQUEST_URL=request_url)
    #     meta_data   = redis_conn.get(meta_key)
    #     content     = redis_conn.get(content_key)
    #     if not (meta_data and content):
    #         return None
    #     result = cls()
    #     for key, value in json.loads(meta_data).items():
    #         setattr(result, key, value)
    #     setattr(result, "content", content)
    #     return result

    def ok(self):
        return self.status
    
    def get_bytes(self):
        return self.content
    
    def get_text(self):
        """
        Quoted from: requests.models.text()
        """
        text = None
        if not self.encoding:
            self.encoding = chardet.detect(self.content)["encoding"]
        try:
            text = str(self.content, self.encoding, errors='replace')
        except (LookupError, TypeError):
            text = str(self.content, errors='replace')
        return text

    def get_json(self, **kwargs):
        """
        Quoted from: requests.models.json()
        """
        if not self.encoding:
            self.encoding = chardet.detect(self.content)["encoding"]
        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using chardet to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return json.loads(
                        self.content.decode(encoding), **kwargs
                    )
                except UnicodeDecodeError:
                    pass
        return json.loads(self.get_text(), **kwargs)
        


class Winney(object):

    def __init__(self, host, port=80, protocol="http", headers=None, redis_host=None, redis_port=None):
        self.host = host
        self.port = port
        self.headers = headers
        self.protocol = protocol
        self.domain = "{}://{}".format(protocol, host)
        if port and port != 80:
            self.domain = self.domain+":"+str(port)
        self.RESULT_FORMATS = ["json", "unicode", "bytes"]
        self.result = {}
        self.apis = []
        self.redis_conn = None
        # if redis_host and redis_port:
        #     self.redis_conn = redis.Redis(host=redis_host, port=redis_port)
    
    def _bind_func_url(self, url, method, cache_time=None):
        def req(data=None, json=None, files=None, headers=None, **kwargs):
            if data and json:
                raise Exception("data 和 json 不可以同时存在")
            url2 = url.format(**kwargs)
            # if cache_time:
            #     r = Result.load_from_cache(url2, method, self.redis_conn)
            #     if r:
            #         return r
            r = self.request(method, url2, data, json, files, headers)
            return Result(r, url2, method, cache_time, self.redis_conn)
        return req
    
    def add_url(self, method, uri, function_name, cache_time=None):
        if not (cache_time is None or isinstance(cache_time, (int, float))):
            raise Exception("cache_time should be None or int or float ,but {} found.".format(type(cache_time)))
        if cache_time is not None and cache_time <= 0:
            raise Exception("cache_time should more than 0, but {} found.".format(cache_time))
        method = method.upper()
        function_name = function_name.lower()
        if function_name in self.apis:
            raise Exception("Duplicate function_name, {}".format(function_name))
        url = urllib.parse.urljoin(self.domain, uri)
        setattr(self, function_name, self._bind_func_url(url, method, cache_time))
        self.apis.append(function_name)
        return getattr(self, function_name)
    
    def request(self, method, url, data=None, json=None, files=None, headers=None):
        if headers and isinstance(headers, dict):
            if self.headers:
                for key, value in self.headers.items():
                    if key in headers:
                        continue
                    headers[key] = value
                # headers.update(self.headers)
        else:
            headers = self.headers
        if method.upper() == "GET":
            return self.get(url, data, headers=headers)
        if method.upper() == "POST":
            return self.post(url, data=data, json=json, files=files, headers=headers)
        if method.upper() == "PUT":
            return self.put(url, data=data, json=json, files=files, headers=headers)

    def get(self, url, data=None, headers=None):
        assert url
        assert (not data or isinstance(data, dict))
        return requests.get(url, params=data, headers=headers)
    
    def post(self, url, data=None, json=None, files=None, headers=None):
        assert url
        assert (not data or isinstance(data, dict))
        assert (not json or isinstance(json, dict))
        return requests.post(url, data=data, json=json, files=files, headers=headers)
    
    def put(self, url, data=None, json=None, files=None, headers=None):
        assert url
        assert (not data or isinstance(data, dict))
        return requests.put(url, data, json=json, files=files, headers=headers)
    
    def delete(self, url, headers=None):
        assert url
        assert (not data or isinstance(data, dict))
        return requests.delete(url, headers=headers)
    
    def options(self, url, headers=None):
        assert url
        assert (not data or isinstance(data, dict))
        return requests.options(url, headers=headers)



if __name__ == "__main__":
    wy = Winney(host="www.baidu.com")
    wy.add_url(method="get", uri="/", function_name="download")
    r = wy.download()
    t = r.get_bytes()
    print(t)
