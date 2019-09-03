#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: requests_wrapper.py
 File Created: Thursday, 14th February 2019 4:20:38 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""


class RequestsWrapper():
    client = None

    def __init__(self, *arg, **args):
        pass
    

    def fetch(self, url, body, method, headers, **request_parameters):
        try:
            if(method == 'GET'):
                return RequestsBodyWrapper(self.client.get(url, data=body, headers=headers))
            else:
                return RequestsBodyWrapper(self.client.post(url, data=body, headers=headers))
        except self.client.exceptions.ConnectionError as e:
            raise ConnectionRefusedError(e)

class RequestsBodyWrapper(object):

    def __init__(self, res):
        self.body = res.text.encode()
        self.code = res.status_code 
        if(res.status_code in (401, 403)):
            e = Exception('Request returned ' + res.status_code, self.body)
            setattr(e, 'code', res.status_code)
            raise e