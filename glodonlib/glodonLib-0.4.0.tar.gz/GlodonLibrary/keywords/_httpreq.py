# coding:utf-8
import json
import traceback

import requests
from requests import Response,Request
from requests.exceptions import (InvalidSchema, InvalidURL, MissingSchema,
                                 RequestException)


class ReqResponse(Response):

    def raise_for_status(self):
        if hasattr(self, 'error') and self.error:
            raise self.error
        Response.raise_for_status(self)


class HttpReq(object):
    s = requests.Session()
    
    def post_with_header(self, data, url, *header):
        """
        接口请求post方法，适用于从配置文件中读取header。
        :param data: 请求参数
        :param url: 接口请求地址
        :param header: 从配置文件中读取获得，格式如：['key']=value
        :return:
        """
        headers = {}
        strDict = 'headers'
        for parameter in header:
            exec (strDict + parameter)
        if not headers:
            r = HttpReq.s.post(url, json = data)
            resultObj = r.text
            return json.loads(resultObj)  # 获取服务器返回的页面信息,转为dict
        else:
            data = json.loads(data)
            try:
                r = HttpReq.s.post(url, headers=headers, json = data)
            except:
                traceback.print_exc()
                raise
            resultObj = r.text
            return json.loads(resultObj)  # 获取服务器返回的页面信息,转为dict
            
    def get_req(self,url,*header):
        """
        接口请求get方法，适用于从配置文件中读取header。
        :param url:
        :param header: 从配置文件中读取获得，格式如：['key']=value
        :return:
        """
        headers = {}
        strDict = 'headers'
        for parameter in header:
            exec (strDict + parameter)
        if not headers:
            r = HttpReq.s.get(url)
            resultObj = r.text
            return json.loads(resultObj)  # 获取服务器返回的页面信息,转为dict
        else:
            try:
                r = HttpReq.s.get(url, headers=headers)
                resultObj = r.text
            except:
                traceback.print_exc()
                raise
            return json.loads(resultObj)
    
    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send an HTTP request, and catch any exception that might occur due to connection problems.
        """
        try:
            return HttpReq.s.request(method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL):
            raise
        except RequestException as e:
            r = ReqResponse()
            r.error = e
            r.status_code = 0  # with this status_code, content returns None
            r.request = Request(method, url).prepare()
            return r

    def rrequest(self, method, url, **kwargs):
        """
        通用请求方法
        :param method: get/post/put/delete
        :param url: 接口请求地址
        :param kwargs:
        :return:
        """
        resp = self._send_request_safe_mode(method, url, **kwargs)
        return resp

    