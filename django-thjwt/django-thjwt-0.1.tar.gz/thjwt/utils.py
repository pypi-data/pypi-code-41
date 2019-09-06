#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/7/25 14:19
# @Author : tianyang@nscc-tj.gov.cn
# @About.:.
# @File : utils.py
# @Site : 
# @Software: PyCharm
from django.utils import timezone as datetime
from django.conf import settings

import re
import requests
import time
import json
import hashlib
from uuid import uuid1
from hashlib import md5
from random import randint

from models import ThiThirdApp,AccessToken,UserLoginToken,CaeAccount

# 生成sid
def generate_sid(appKey,timeStamp):
    print("appKey =%s and timeStamp=%s" % (appKey,timeStamp))
    sid = md5(appKey + timeStamp).hexdigest()
    return sid

# 验证sid
def check_sid(appId,sid,timeStamp):
    tApp = ThiThirdApp.objects.filter(appId=appId).first()
    if not tApp:
        print("no this appid's app")
        return False
    if not sid == generate_sid(tApp.appKey,timeStamp):
        print("sid=%s check sid = %s" % (sid,generate_sid(tApp.appKey,timeStamp)))
        return False
    return True

# 替换字符串
def sub(string, p, c):
    new = []
    for s in string:
        new.append(s)
    new[p] = c
    return ''.join(new)

# 生成accessToken
def gen_access_token():
    u = str(uuid1())
    s = md5(u).hexdigest()
    for x in xrange(len(s) / 3):
        n = randint(1, len(s) - 1)
        if s[n].isalpha():
            s = sub(s,n,s[n].upper())
    return s

# 生成客户端accessToken
def generate_access_token(appId):
    s = gen_access_token()
    app = ThiThirdApp.objects.filter(appId=appId).first()
    accessToken = AccessToken.objects.filter(thiThirdApp=app).first()
    now = datetime.now()
    if not accessToken:
        accessToken = AccessToken(thiThirdApp=app,accessToken=s,updateTime=now)
        accessToken.save()
    else:
        accessToken.delete()
        accessToken = AccessToken(thiThirdApp=app, accessToken=s, updateTime=now)
        accessToken.save()
    return s

# 更新accessToken
def update_access_token(accessToken,appId):
    now = datetime.now()
    accessToken = AccessToken.objects.filter(accessToken=accessToken).first()
    if not accessToken:
        return False
    else:
        s =generate_access_token(appId)
        accessToken.accessToken = s
        accessToken.updateTime = now
    return True

#检查accessToken
def check_access_token(accessToken):
    accessToken = AccessToken.objects.filter(accessToken=accessToken).first()
    if not accessToken:
        return {"success":"no","errorCode":7,"errorDesc":"access token is not exist"}
    if (accessToken.updateTime - datetime.now()).total_seconds() > settings.TOKEN_EXPIRED_TIME:
        return {"success": "no", "errorCode": 8, "errorDesc": "access token is expired"}
    return {"success":"yes"}

# 通过accessToken查找accountName
def get_account_from_access_token(accessToken):
    at = AccessToken.objects.filter(accessToken=accessToken).first()
    caeAccount = CaeAccount.objects.filter(thiThirdApp=at.thiThirdApp).first()
    return caeAccount

# 用户名格式正则校验，只允许字母、数字、下划线
def check_username_validity(userName):
    STR_REGEX = r'^(\w)+$'
    if re.match(STR_REGEX, userName) is None:
        return False
    else:
        return True

# 检查用户名合法性
def check_user_name(userName, accessToken):
    if userName is None:
        return False
    if check_username_validity(userName):
        maxLength = 12
        caeAccount = get_account_from_access_token(accessToken)
        if caeAccount:
            maxLength = maxLength - len(caeAccount.userNameSuffix) - 1
            if len(userName) >= 4 and len(userName) <= maxLength:
                return True
    return False

# 生成中间层用户名
def generate_middle_user_name(userName, accessToken):
    caeAccount = get_account_from_access_token(accessToken)
    if caeAccount:
        return userName + '_' + caeAccount.userNameSuffix
    else:
        return False

# 仿真中间层接口验证url
def generate_cae_api_url(apiUrl):
    timeStamp = str(int(time.time()))
    sid = md5(settings.COMPUTE_API_KEY + str(timeStamp)).hexdigest()
    url = "{urlHost}{apiUrl}?appid={appId}&sid={sid}&timestamp={timeStamp}".format(urlHost=settings.COMPUTE_API_HOST,
                                                                                   apiUrl=apiUrl,
                                                                                   appId=settings.COMPUTE_API_ID,
                                                                                   sid=sid,
                                                                                   timeStamp=timeStamp)
    return url

# 仿真中间层API查询用户是否存在 需确保该appid的account已经存在并存储在CaeAccount中
def is_cae_user(userName,accessToken):
    url = generate_cae_api_url("/cae/user")
    caeAccount = get_account_from_access_token(accessToken)
    userName = generate_middle_user_name(userName,accessToken)
    data = {"username":userName,"accountname":caeAccount.accountName}
    r = requests.get(url,params=data)
    if r.json().get('success') == "yes":
        return True
    else:
        return False

# 生成login token
def generate_user_login_token(userName, accessToken,displayUserName):
    u = uuid1()
    loginToken = md5(str(u) + userName + accessToken).hexdigest()
    userLoginToken = UserLoginToken.objects.filter(userName=userName).first()
    aT = AccessToken.objects.filter(accessToken=accessToken).first()
    now = datetime.now()
    if not is_cae_user(userName,accessToken):
        return False
    if not userLoginToken:
        userLoginToken = UserLoginToken(loginToken=loginToken,userName=userName,updateTime=now,thiThirdApp=aT.thiThirdApp,displayUserName=displayUserName)
    else:
        userLoginToken.loginToken = loginToken
        userLoginToken.updateTime = now
    userLoginToken.save()
    return loginToken

# 根据loginToken 查找 用户
def check_user_login_token(loginToken):
    res = {"error":"undifined"}
    userLoginToken = UserLoginToken.objects.filter(loginToken=loginToken).first()
    caeAccount = CaeAccount.objects.filter(thiThirdApp=userLoginToken.thiThirdApp).first()
    if userLoginToken:
        res['username'] = userLoginToken.userName
        res['displayUserName'] = userLoginToken.displayUserName
        res['userNameSuffix'] = caeAccount.userNameSuffix
        res['accountName'] = caeAccount.accountName
        del res['error']
        userLoginToken.delete()
    else:
        res['error'] = "loginToken is invalid"
    return res

# 中间层接口调用
def middleware_api_call(api, url, data, method):
    timeStamp = str(time.time())
    if "compute" == api:
        sid = hashlib.md5(settings.COMPUTE_API_KEY + timeStamp).hexdigest()
        sendUrl = settings.COMPUTE_API_HOST + url + "?appid=" + settings.COMPUTE_API_ID + "&sid=" + sid + "&timestamp=" + timeStamp
    elif "storage" == api:
        sid = hashlib.md5(settings.STORAGE_API_KEY + timeStamp).hexdigest()
        sendUrl = settings.STORAGE_API_HOST + url + "?appid=" + settings.STORAGE_API_ID + "&sid=" + sid + "&timestamp=" + timeStamp
    elif "visual" == api:
        sid = hashlib.md5(settings.VISUAL_API_KEY + timeStamp).hexdigest()
        sendUrl = settings.VISUAL_API_HOST + url + "?appid=" + settings.VISUAL_API_ID + "&sid=" + sid + "&timestamp=" + timeStamp
    else:
        return False

    if "get" == method:
        res = requests.get(sendUrl, params=data)
    elif "post" == method:
        res = requests.post(sendUrl, data=json.dumps(data))
    elif "put" == method:
        res = requests.put(sendUrl, data=json.dumps(data))
    elif "delete" == method:
        res = requests.delete(sendUrl, data=json.dumps(data))
    else:
        res = None

    print res.json()

    return res.json()

# 计算账户已分配总核数
def compute_account_used_quota(accountUsers):
    # 账户已分配给用户的总核数 = 各用户核数之和
    usedCpuQuota = 0
    for user in accountUsers:
        usedCpuQuota += user['quota']
    return usedCpuQuota

# 调用存储中间层取到用户存储配额，跟其他计算中检测信息一起序列化
def compute_info_serializers_storage_quota(accountUsers):
    users = list()
    accountUsers = filter(lambda x:x['authority'] != 'admin',accountUsers)
    for user in accountUsers:
        storageUrl = "/users/" + user['username']
        storageParam = {}
        userStorageRes = middleware_api_call("storage", storageUrl, storageParam, "get")
        if userStorageRes['success'] == 'no':
            userStorageRes['userinfo'] = {'quota':0}
        storageQuota = userStorageRes['userinfo']['quota']
        users.append({
                'userName': "".join(user['username'].split('_')[:-1]), 'userType': user['type'], 'cpuTime': float('%.2f' % (float(user['cputimes']) / 3600)),
                'cpuQuota': user['quota'], 'storageQuota': storageQuota
        })
    return users

# 用户类型校验
def check_user_type(userType):
    if userType is None:
        return False
    elif "formal" != userType and "test" != userType:
        return False
    else:
        return True

# 创建计算用户
def create_compute_user(userName, userType, accountName):
    data = {'username': userName, 'type': userType, 'accountname': accountName}
    userRes = middleware_api_call("compute", "/cae/user", data, "post")
    if 'yes' == userRes['success']:
        return userRes['userinfo']
    else:
        return False

# 删除计算用户
def delete_compute_user(userName):
    data = {'username': userName}
    userRes = middleware_api_call("compute", "/cae/user", data, "delete")
    if 'no' == userRes['success']:
        return False
    else:
        return True

# 创建存储用户
def create_storage_user(userName):
    storageUrl = "/users/" + userName
    storageParam = {"quota":500}
    userStorageRes = middleware_api_call("storage", storageUrl, storageParam, "post")
    if 'yes' == userStorageRes['success']:
        return userStorageRes['userinfo']
    else:
        return False

# 删除存储用户
def delete_storage_user(userName):
    storageUrl = "/users/" + userName
    storageParam = {}
    userStorageRes = middleware_api_call("storage", storageUrl, storageParam, "delete")
    if 'yes' == userStorageRes['success']:
        return True
    else:
        return False

# 创建可视化用户
def create_visual_user(userName):
    visualUrl = "/user/" + userName
    visualParam = {}
    userVisualRes = middleware_api_call("visual", visualUrl, visualParam, "post")
    if 'yes' == userVisualRes['success']:
        return True
    else:
        return False

# 删除可视化用户
def delete_visual_user(userName):
    visualUrl = "/user/" + userName
    visualParam = {}
    userVisualRes = middleware_api_call("visual", visualUrl, visualParam, "delete")
    if 'yes' == userVisualRes['success']:
        return True
    else:
        return False

# 查询账户下所有用户
def get_all_users(accountName):
    data = {"accountname": accountName}
    accountUsersRes = middleware_api_call("compute", "/cae/accountusers", data, "get")
    if 'yes' == accountUsersRes['success']:
        return accountUsersRes['accountusers']
    else:
        return False

# 用户数查询
def get_users_count(accountName):
    accountUsersRes = get_all_users(accountName)
    usersCount = -1
    if accountUsersRes:
        for user in accountUsersRes:
            usersCount += 1
    return usersCount

# 查询用户信息
def get_user_info(userName):
    storageUrl = "/users/" + userName
    storageParam = {}
    userStorageRes = middleware_api_call("storage", storageUrl, storageParam, "get")
    if userStorageRes['success'] == 'no':
        userStorageRes['userinfo'] = {'quota': 0}
    storageQuota = userStorageRes['userinfo']['quota']
    computeParam = {'username':userName}
    userComputeRes = middleware_api_call("compute", "/cae/user", computeParam, "get")
    if 'no' == userComputeRes['success']:
        return {'error':userComputeRes['error_desc'],'res':False}
    else:
        userInfo = userComputeRes['userinfo']
        userInfo = {
            'userName': "".join(userInfo['username'].split('_')[:-1]), 'userType': userInfo['type'],
            'cpuTime': float('%.2f' % (float(userInfo['cputimes']) / 3600)),
            'cpuQuota': userInfo['quota'], 'storageQuota': storageQuota
        }
    return {'userInfo':userInfo,'res':True}

# 求机时秒数函数
def get_seconds(cpuTime):
    seconds = 0
    day = 0
    try:
        day = int(cpuTime.split('-')[-2])
        tl = cpuTime.split('-')[-1].split('-1')[-1].split(":")
    except:
        tl = cpuTime.split('-1')[-1].split(":")

    seconds = day * 3600 * 24 + 3600 * int(tl[0]) + 60 * int(tl[1]) + int(tl[2])
    return seconds

# 查询账户作业,并计算总机时
def account_jobs_list(accountName,detail,startTime,endTime,userName,status,jobName,serviceType):
    data = {'accountname':accountName}
    if detail != 0:
        data['detail'] = 'yes'
    if startTime:
        data['starttime'] = startTime.replace(" ", "-")
    if endTime:
        data['endtime'] = endTime.replace(" ", "-")
    accountJobsListRes = middleware_api_call("compute", "/cae/historytasksaccount", data, "get")
    if 'no' == accountJobsListRes['success']:
        return {'error':accountJobsListRes['error_desc'],'res':False}
    else:
        if detail == 0:
            return {
                'jobsCount':accountJobsListRes['jobcount'],
                'runningJobsCount':accountJobsListRes['running_jobcount'],
                'overJobsCount':accountJobsListRes['over_jobcount']
            }
        jobsList = list()
        try:
            accountJobsList = accountJobsListRes['jobs']
            scaleCpuTime = 0.0
            resourceCpuTime = 0.0
            for i in accountJobsList:
                for job in accountJobsList[i]['joblist']:
                    jobsList.append(job)
                    if job['statusdetail']:
                        if job['charge_type'] =='real_resource':
                            # totalCpuTime += get_seconds(job['statusdetail']['CPUTime'])
                            resourceCpuTime += (get_seconds(job['statusdetail']['Elapsed']) * float(job['statusdetail']['ReqCPUS']))
                        elif job['charge_type'] =='limit_scale':
                            scaleCpuTime += (get_seconds(job['statusdetail']['Elapsed']) * float(job['statusdetail']['ReqCPUS']))
                # userJobList = {i : userJob}
                # jobsList.append(userJobList)

            # 条件过滤
            if userName:
                jobsList = filter(lambda x: x['username'] in userName, jobsList)
            if status:
                jobsList = filter(lambda x: x['status'] in status, jobsList)
            if jobName:
                jobsList = filter(lambda x: jobName in x['jobname'], jobsList)
            if serviceType:
                jobsList = filter(lambda x: x['charge_type'] == serviceType, jobsList)

            resourceCpuTime = float('%.2f' % (resourceCpuTime / 3600))
            scaleCpuTime = float('%.2f' % (scaleCpuTime / 3600))
            jobsRes = {
                'resourceCpuTime': resourceCpuTime,'scaleCpuTime':scaleCpuTime, 'jobs':jobsList,
                'jobsCount': accountJobsListRes['jobcount'],
                'runningJobsCount': accountJobsListRes['running_jobcount'],
                'overJobsCount': accountJobsListRes['over_jobcount']
            }
        except KeyError as ke:
            jobsRes = {
                'resourceCpuTime': 0.0,'scaleCpuTime':0.0,'jobs':{},
                'jobsCount': accountJobsListRes['jobcount'],
                'runningJobsCount': accountJobsListRes['running_jobcount'],
                'overJobsCount': accountJobsListRes['over_jobcount']
            }
        return jobsRes

# 查询用户作业
def user_jobs_list(userName,detail,startTime,endTime,status,jobName,serviceType):
    data = {'username': userName}
    if detail != 0:
        data['detail'] = "yes"
    if startTime:
        data['starttime'] = startTime
    if endTime:
        data['endtime'] = endTime
    # userJobsList = middleware_api_call("compute", "/cae/tasks", data, "get")
    userJobsListRes = middleware_api_call("compute", "/cae/historytasksuser", data, "get")
    if 'no' == userJobsListRes['success']:
        return {'error':userJobsListRes['error_desc'],'res':False}
    else:
        if detail == 0:
            return {'allJobsCount' : userJobsListRes['all_jobcount'],'res':True}
        try:
            userJobsList = list()
            scaleCpuTime = 0.0
            resourceCpuTime = 0.0
            userAllJobs = userJobsListRes['all_jobs']
            overJobsCount = userJobsListRes['over_jobcount']
            runningJobsCount = userJobsListRes['running_jobcount']

            for user in userAllJobs:
                userJob = user['statusdetail']
                if userJob:
                    if user['charge_type'] == 'real_resource':
                        # totalCpuTime += get_seconds(job['statusdetail']['CPUTime'])
                        resourceCpuTime += (
                                    get_seconds(userJob['Elapsed']) * float(userJob['ReqCPUS']))
                    elif user['charge_type'] == 'limit_scale':
                        scaleCpuTime += (
                                    get_seconds(userJob['Elapsed']) * float(userJob['ReqCPUS']))
                userJobsList.append(user)

            # 条件过滤
            if status:
                userJobsList = filter(lambda x: x['status'] in status, userJobsList)
            if jobName:
                userJobsList = filter(lambda x: jobName in x['jobname'], userJobsList)
            if serviceType:
                userJobsList = filter(lambda x: x['charge_type'] == serviceType, userJobsList)

            resourceCpuTime = float('%.2f' % (resourceCpuTime / 3600))
            scaleCpuTime = float('%.2f' % (scaleCpuTime / 3600))
            jobsList = {'resourceCpuTime': resourceCpuTime,'scaleCpuTime':scaleCpuTime,'jobs':userJobsList,'overJobsCount':overJobsCount,'runningJobsCount':runningJobsCount}
        except KeyError as ke:
            jobsList = {'resourceCpuTime': 0.0,'scaleCpuTime':0.0,'jobs':{},'overJobsCount':0,'runningJobsCount':0}
        return jobsList

# 查询账户总机时和核数配额
def get_account_total_quota(accountName):
    data = {"accountname": accountName}
    accountRes = middleware_api_call("compute", "/cae/account", data, "get")
    if 'yes' == accountRes['success']:
        accountCpuTime = float(accountRes['accountinfo']['cputime'] / 3600)
        accountCpuQuota = accountRes['accountinfo']['scale']
        return {'accountCpuTime':accountCpuTime,'accountCpuQuota':accountCpuQuota}
    else:
        return False

# 重置：查询账户下其他用户的cpuTime之和
# 增量：查询账户下所有用户的cpuTime之和
def get_users_total_cputime(accountName, userName, operation):
    accountUsersRes = get_all_users(accountName)
    totalCpuTime = 0
    if accountUsersRes:
        for accountUser in accountUsersRes:
            if (operation != "set") or (userName != accountUser['username']):
                totalCpuTime += float('%.2f' % (float(accountUser['cputimes']) / 3600))
    return totalCpuTime

# 判断：
# 重置：用户要重置的机时配额 + 其他用户机时配额 < 账户总机时配额?
# 增量：用户要增量的机时配额 + 所有用户机时配额 < 账户总机时配额?
def check_cpu_time_excess(accountName, userName ,userCpuTime, operation):
    accountCpuTime = get_account_total_quota(accountName)['accountCpuTime']
    usersTotalCpuTime = get_users_total_cputime(accountName, userName, operation)
    if accountCpuTime is False or usersTotalCpuTime is False:
        return {'error':'Get middleware data failed','res':False}
    else:
        userCpuTimeF = float(userCpuTime)

        if (userCpuTimeF + usersTotalCpuTime) > accountCpuTime:
            return {'error':'CpuTime excess','res':False}
        else:
            return {'res':True}

# 判断：
# 重置：用户要重置的核数配额 < 账户总核数配额？
# 增量：用户原核数配额 + 用户要增加的核数配额 < 账户总核数配额？
def check_cpu_quota_excess(accountName, userName, cpuQuota, operation):
    accountCpuQuota = get_account_total_quota(accountName)['accountCpuQuota']
    if accountCpuQuota is False:
        return {'error':'Get middleware data failed','res':False}
    else:
        cpuQuotaI = int(cpuQuota)
        if (cpuQuotaI % 28) != 0:
            return {'error': 'CpuQuota must be an integer multiple of 28', 'res': False}
        if operation == "set":
            if cpuQuotaI > accountCpuQuota:
                return {'error':'CpuQuota excess','res':False}
            else:
                return {'res': True}
        elif operation == "add":
            try:
                selfCpuQuota = int(get_user_info(userName).get('userInfo').get('cpuQuota'))
            except ValueError:
                return {'error': 'User not exist', 'res': False}
            except AttributeError:
                return {'error': 'User not exist', 'res': False}
            if selfCpuQuota + cpuQuotaI > accountCpuQuota:
                return {'error':'CpuQuota excess','res':False}
            else:
                return {'res': True}

# 修改用户计算资源（机时 or 核数）
def update_compute_resource(userName, userType, cpuTime, cpuQuota, operation):
    data = {'username':userName,'type': userType,'operation':operation}
    if cpuTime:
        data['cputime'] = long(float(cpuTime) * 3600)
    if cpuQuota:
        data['quota'] = int(cpuQuota)
    updateRes = middleware_api_call("compute", "/cae/user", data, "put")
    if 'yes' == updateRes['success']:
        userInfo = {
            'userName':updateRes['userinfo']['username'],'userType':updateRes['userinfo']['type'],
            'cpuTime':float('%.2f' % (updateRes['userinfo']['cputimes_uplimit'] / 3600)),'cpuQuota':updateRes['userinfo']['cpus_uplimit'],
        }
        return {'userInfo':userInfo,'res':True}
    else:
        return {'error':'Update compute resource failed: ' + updateRes['error_desc'],'res':False}

# 修改用户存储资源（存储配额）
def update_storage_resource(userName, storageQuota):
    storageUrl = "/users/" + userName
    storageParam = {'quota':storageQuota}
    updateRes = middleware_api_call("storage", storageUrl, storageParam, "put")
    if 'yes' == updateRes['success']:
        return {'storageQuota':updateRes['userinfo']['quota'],'res':True}
    else:
        return {'error': 'Update storage resource failed', 'res': False}
