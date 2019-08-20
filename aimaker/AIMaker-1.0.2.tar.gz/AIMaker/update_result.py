import os
import requests
import json

KEY_RESULT_VALUE = "result"

def sendUpdateRequest(c):
    try:
        job = os.environ['AI_MAKER_JOB_ID']
        param = os.environ['AI_MAKER_PARAM_ID']
        token = os.environ['AI_MAKER_TOKEN']
        url = os.environ['AI_MAKER_HOST']
    except KeyError as e:
        print ("[KeyError] Please assign {} value".format(str(e)))
        return -1
    HEADERS = {"content-type" : "application/json",
               "Authorization" : token}
    body = json.dumps({ KEY_RESULT_VALUE : c })
    url = url+"/api/v1/ai-maker/callback/results/jobs/"+job+"/params/"+param
    return requests.post(url, data = body, headers = HEADERS)

def saveValidationResult(result):
    try:
        job = os.environ['AI_MAKER_JOB_ID']
        model = os.environ['AI_MAKER_MODEL_ID']
        token = os.environ['AI_MAKER_TOKEN']
        url = os.environ['AI_MAKER_HOST']
    except KeyError as e:
        print ("[KeyError] Please assign {} value".format(str(e)))
        return -1
    HEADERS = {"content-type" : "application/json",
               "Authorization" : token}
    body = json.dumps({ KEY_RESULT_VALUE : result })
    url = url+"/api/v1/ai-maker/callback/results/jobs/"+job+"/models/"+model+"/validations"
    return requests.post(url, data = body, headers = HEADERS)
