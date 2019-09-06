#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/7/25 15:25
# @Author : tianyang@nscc-tj.gov.cn
# @About.:.
# @File : middleware.py
# @Site : 
# @Software: PyCharm
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse,HttpResponse
from django.http import QueryDict
from utils import *
import json

class CheckTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path_arr = filter(lambda x:x!='',request.path.split('/'))
        if not path_arr:
            return JsonResponse({"error":"Url not Found"},status=404)
        if path_arr[0] == "admin":
            return None
        if len(path_arr) < 3:
            return None
        if path_arr[2] in ['access_token','user_login'] or path_arr[3] in ['access_token','user_login']:
            return None
        if request.method == "GET":
            accessToken = request.GET.get("accessToken", "")
        else:
            qData = QueryDict(mutable=True)
            qData.update(json.loads(request.body))
            accessToken = qData.get("accessToken","")
        if accessToken == "":
            return JsonResponse({"error":"accessToken can not be null"},status=401)
        res = check_access_token(accessToken)
        if res.get("success") == "no":
            return HttpResponse('Invalid accessToken',status=401)
        else:
            return None

class RestfulRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'GET':
            return None
        try:
            qData = QueryDict(mutable=True)
            qData.update(json.loads(request.body))
            setattr(request, request.method, qData)
        except BaseException as e:
            return HttpResponse('Invalid request data format',status=400)
        return None