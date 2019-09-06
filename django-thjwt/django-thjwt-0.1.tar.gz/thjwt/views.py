# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse,HttpResponse
from django.http import HttpResponseNotAllowed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils import *

# Create your views here.
def get_access_token(request):
    if request.method == 'POST':
        accessTokenInfo = {
            "error":"undefined"
        }
        appId = request.POST.get("appId","")
        sid = request.POST.get("sid","")
        timeStamp = request.POST.get("timeStamp","")

        if not check_sid(appId,sid,timeStamp):
            accessTokenInfo['error'] = 'sid is not right'
            return JsonResponse(accessTokenInfo,status=401)
        else:
            accessToken = generate_access_token(appId)
            del accessTokenInfo['error']
            accessTokenInfo['accessToken'] = accessToken
            accessTokenInfo['expireTime'] = settings.ACCESS_TOKEN_EXPIRED_TIME * 60
            return JsonResponse(accessTokenInfo, status=200)
    elif request.method == "PUT":
        accessTokenInfo = {
            "error": "undefined"
        }
        accessToken = request.PUT.get('accessToken', '')
        appId = request.PUT.get("appId", "")
        accessToken = update_access_token(accessToken,appId)
        if accessToken:
            accessTokenInfo['accessToken'] = accessToken
            accessTokenInfo['expireTime'] = settings.ACCESS_TOKEN_EXPIRED_TIME * 60
            return JsonResponse(accessTokenInfo, status=200)
        else:
            accessTokenInfo['error'] = "acess token not right"
            return HttpResponse(status=401)
    return HttpResponse(status=405)

def get_user_login_token(request):
    if request.method == "POST":
        userLoginInfo = {
            "error": "undefined"
        }
        accessToken = request.POST.get('accessToken', '')
        userName = request.POST.get('userName','')
        displayUserName = request.POST.get('displayUserName',userName)
        if not check_user_name(userName, accessToken):
            userLoginInfo['error'] = "userName invalid"
            return JsonResponse(userLoginInfo, status=422)
        else:
            loginToken = generate_user_login_token(userName, accessToken, displayUserName)
            if not loginToken:
                return JsonResponse({'error':'User not exist'},status=422)
            userLoginInfo['loginToken'] = loginToken
            del userLoginInfo['error']
            return JsonResponse(userLoginInfo, status=200)
    return HttpResponseNotAllowed(405)

def user_login(request):
    if request.method == 'POST':
        loginToken = request.POST.get("loginToken","")
        res = check_user_login_token(loginToken)
        if 'error' in res.keys():
            return JsonResponse(res, status=403)
        else:
            return JsonResponse(res,status=200)
    return HttpResponseNotAllowed({'error':"method not allowed"},status=405)

# 查询账户接口
def get_account_info(request):
    if request.method == 'GET':
        accessToken = request.GET.get("accessToken")
        accountName = get_account_from_access_token(accessToken).accountName
        data = {"accountname": accountName}
        accountRes = middleware_api_call("compute", "/cae/account", data, "get")
        accountUsersRes = middleware_api_call("compute", "/cae/accountusers", data, "get")
        if 'yes' == accountUsersRes['success']:
            usedCpuQuota = compute_account_used_quota(accountUsersRes['accountusers'])
        else:
            return JsonResponse({'error': 'Middleware <account users quota> invaild'}, status=422)
        if 'yes' == accountRes['success']:
            return JsonResponse({
                'cpuTime': float(accountRes['accountinfo']['cputime'] / 3600),
                'usedCpuTime': float(accountRes['accountinfo']['usedcputime'] / 3600),
                'cpuQuota': accountRes['accountinfo']['scale'],
                'usedCpuQuota': usedCpuQuota,
            })
        else:
            return JsonResponse({'error': 'Middleware <account info> invaild'}, status=422)
    else:
        return JsonResponse({'error':'Method not allowed'},status=405)

# 用户列表接口
def get_users_list(request):
    if request.method == 'GET':
        accessToken = request.GET.get("accessToken")
        accountName = get_account_from_access_token(accessToken).accountName
        accountUsersRes = get_all_users(accountName)
        if accountUsersRes:
            serializersRes = compute_info_serializers_storage_quota(accountUsersRes)
            if not serializersRes:
                return JsonResponse({'error': 'Middleware <users storage> invaild'}, status=422)
            else:
                return JsonResponse({'users': serializersRes})
        else:
            return JsonResponse({'error': 'Middleware <account users> invaild'}, status=422)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# 用户管理接口 (增删改查)
def user_manager(request):
    # 创建用户接口
    if request.method == 'POST':
        accessToken = request.POST.get("accessToken")
        userName = request.POST.get("userName")
        userType = request.POST.get("userType")

        if not check_user_name(userName, accessToken):
            return JsonResponse({'error': "Bad userName"}, status=400)
        if not check_user_type(userType):
            return JsonResponse({'error': "UserType invalid"}, status=400)

        accout = get_account_from_access_token(accessToken)
        accountName = accout.accountName
        if get_users_count(accountName) > settings.MAX_USERS_COUNT_LIMITION:
            return JsonResponse({'error': "Create users too many, limition: %d" % settings.MAX_USERS_COUNT_LIMITION},
                                status=422)
        userName = generate_middle_user_name(userName, accessToken)
        if not accountName:
            return JsonResponse({'error': "Get accout name failed"}, status=422)

        createComputeUserRes = create_compute_user(userName, userType, accountName)
        if not createComputeUserRes:
            return JsonResponse({'error': 'Create compute user failed'}, status=422)
        createStorageUserRes = create_storage_user(userName)
        if not createStorageUserRes:
            if delete_compute_user(userName):
                return JsonResponse({'error': 'Create storage user failed, Revert compute user done'}, status=422)
            else:
                return JsonResponse({'error': 'Create storage user failed, Revert compute user failed'}, status=422)
        createVisualUserRes = create_visual_user(userName)
        if not createVisualUserRes:
            if delete_compute_user(userName):
                if delete_storage_user(userName):
                    return JsonResponse(
                        {'error': 'Create visual user failed, Revert compute user done, Revert storage user done'},
                        status=422)
                else:
                    return JsonResponse(
                        {'error': 'Create visual user failed, Revert compute user done, Revert storage user failed'},
                        status=422)
            else:
                if delete_storage_user(userName):
                    return JsonResponse(
                        {'error': 'Create visual user failed, Revert compute user failed, Revert storage user done'},
                        status=422)
                else:
                    return JsonResponse(
                        {'error': 'Create visual user failed, Revert compute user failed, Revert storage user failed'},
                        status=422)
        return HttpResponse(status=201)

    # 查询用户接口
    elif request.method == 'GET':
        accessToken = request.GET.get("accessToken")
        userName = request.GET.get("userName")

        if not check_user_name(userName, accessToken):
            return JsonResponse({'error': "Bad userName"}, status=400)

        accout = get_account_from_access_token(accessToken)
        accountName = accout.accountName
        userName = generate_middle_user_name(userName, accessToken)
        if not accountName:
            return JsonResponse({'error': "Get accout name failed"}, status=422)

        getUserInfoRes = get_user_info(userName)
        if getUserInfoRes.get('res') is False:
            return JsonResponse({'error': "Get user info failed"}, status=422)
        else:
            return JsonResponse(getUserInfoRes.get('userInfo'))

    # 修改用户接口
    elif request.method == 'PUT':
        accessToken = request.PUT.get("accessToken")
        userName = request.PUT.get("userName")
        userType = request.PUT.get("userType","test")
        operation = request.PUT.get("operation","set")
        cpuTime = request.PUT.get("cpuTime")
        cpuQuota = request.PUT.get("cpuQuota")
        storageQuota = request.PUT.get("storageQuota")

        accout = get_account_from_access_token(accessToken)
        accountName = accout.accountName
        userName = generate_middle_user_name(userName, accessToken)

        # 超额校验
        if cpuTime:
            checkCpuTimeExcessRes = check_cpu_time_excess(accountName, userName ,cpuTime, operation)
            if not checkCpuTimeExcessRes['res']:
                return JsonResponse({'errorr':checkCpuTimeExcessRes['error']}, status=422)
        if cpuQuota:
            checkCpuQuotaExcessRes = check_cpu_quota_excess(accountName, userName, cpuQuota, operation)
            if not checkCpuQuotaExcessRes['res']:
                return JsonResponse({'errorr':checkCpuQuotaExcessRes['error']}, status=422)
        if not check_user_name(userName, accessToken):
            return JsonResponse({'error': "Bad userName"}, status=400)
        if not check_user_type(userType):
            return JsonResponse({'error': "UserType invalid"}, status=400)

        updateComputeRes = update_compute_resource(userName, userType, cpuTime, cpuQuota, operation)
        if not updateComputeRes['res']:
            return JsonResponse({'error': updateComputeRes['error']}, status=422)
        updateRes = updateComputeRes['userInfo']

        if storageQuota:
            storageQuota = float(storageQuota)
            if (storageQuota < 0) or (storageQuota > 1000.0):
                return JsonResponse({'error': "storageQuota excess"}, status=422)
            if operation == "set":
                updateStorageRes = update_storage_resource(userName, storageQuota)
                if not updateStorageRes['res']:
                    return JsonResponse({'errorr': updateStorageRes['error']}, status=422)
                updateRes['storageQuota'] = updateStorageRes['storageQuota']

        return JsonResponse(updateRes,status=201)

    # 删除用户接口
    elif request.method == 'DELETE':
        accessToken = request.DELETE.get("accessToken")
        userName = request.DELETE.get("userName")

        userName = generate_middle_user_name(userName, accessToken)

        detleteVisualUserRes = delete_visual_user(userName)
        if not detleteVisualUserRes:
            return JsonResponse({'error': "Delete visual user failed"}, status=422)
        detleteStorageUserRes = delete_storage_user(userName)
        if not detleteStorageUserRes:
            return JsonResponse({'error': "Delete storage user failed"}, status=422)
        detleteComputeUserRes = delete_compute_user(userName)
        if not detleteComputeUserRes:
            return JsonResponse({'error': "Delete compute user failed"}, status=422)

        return HttpResponse(status=204)

    else:
        return HttpResponseNotAllowed("method not allowed")

# 查询账户作业接口
def get_accout_jobs(request):
    if request.method == 'GET':
        accessToken = request.GET.get("accessToken")
        page = request.GET.get("page",1)
        pageCount = request.GET.get("pageCount",200)
        detail = int(request.GET.get("detail",0))
        startTime = request.GET.get("startTime")
        endTime = request.GET.get("endTime")

        userName = request.GET.getlist("userName")
        status = request.GET.getlist("status")
        jobName = request.GET.get("jobName")
        serviceType = request.GET.get("serviceType")

        accout = get_account_from_access_token(accessToken)
        accountName = accout.accountName
        # accountName = "tjfaw2016"
        if not accountName:
            return JsonResponse({'error': "Get accout name failed"}, status=422)
        if userName:
            userName = map(lambda x:generate_middle_user_name(x, accessToken),userName)

        jobsList = account_jobs_list(accountName,detail,startTime,endTime,userName,status,jobName,serviceType)
        if detail == 0:
            return JsonResponse({
                'jobsCount':jobsList['jobsCount'],
                'runningJobsCount': jobsList['runningJobsCount'],
                'overJobsCount': jobsList['overJobsCount']
            })
        if jobsList.get('res') is False:
            return JsonResponse({'error': jobsList.get('error')}, status=422)
        paginator = Paginator(jobsList['jobs'], pageCount)
        totalPage = paginator.num_pages
        jobsCount = paginator.count
        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            jobs = paginator.page(1)
        except EmptyPage:
            jobs = paginator.page(paginator.num_pages)
        return JsonResponse({
            'resourceCpuTime':jobsList['resourceCpuTime'],
            'scaleCpuTime': jobsList['scaleCpuTime'],
            'jobs': jobs.object_list,
            'pages':totalPage,
            'jobsCount':jobsCount,
            'runningJobsCount': jobsList['runningJobsCount'],
            'overJobsCount': jobsList['overJobsCount']
        })
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# 查询用户作业接口
def get_user_jobs(request):
    if request.method == 'GET':
        accessToken = request.GET.get("accessToken")
        userName = request.GET.get("userName")
        page = request.GET.get("page",1)
        pageCount = request.GET.get("pageCount",200)
        detail = int(request.GET.get("detail",0))
        startTime = request.GET.get("startTime")
        endTime = request.GET.get("endTime")

        status = request.GET.getlist("status")
        jobName = request.GET.get("jobName")
        serviceType = request.GET.get("serviceType")

        accout = get_account_from_access_token(accessToken)
        accountName = accout.accountName
        userName = generate_middle_user_name(userName, accessToken)
        if not accountName:
            return JsonResponse({'error': "Get accout name failed"}, status=422)

        jobsList = user_jobs_list(userName,detail,startTime,endTime,status,jobName,serviceType)
        if jobsList.get('res') is False:
            return JsonResponse({'error': jobsList.get('error')}, status=422)
        if detail == 0:
            return JsonResponse({'jobsCount':jobsList['allJobsCount']})
        paginator = Paginator(jobsList['jobs'], pageCount)
        totalPage = paginator.num_pages
        jobsCount = paginator.count
        try:
            jobs = paginator.page(page)
        except PageNotAnInteger:
            jobs = paginator.page(1)
        except EmptyPage:
            jobs = paginator.page(paginator.num_pages)
        return JsonResponse({
            'jobs':jobs.object_list,
            'resourceCpuTime': jobsList['resourceCpuTime'],
            'scaleCpuTime': jobsList['scaleCpuTime'],
            'page':totalPage,
            'jobsCount':jobsCount,
            'overJobsCount':jobsList['overJobsCount'],
            'runningJobsCount': jobsList['runningJobsCount'],
        })
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)