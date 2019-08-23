import requests
import json

def parseResponse(r,printResult = True, parseJSON = True):
    if r.status_code == 200:
        if printResult:
            print('response: ',r.text)
        if parseJSON:
            return json.loads(r.text)
        else: 
            return
    else:
        raise RuntimeError(r.text)

def send(url,payload,printPayload = True,printResult = True):

    payload = {k: v for k, v in payload.items() if v!= '' and v != None } # clean None inputs
    if printPayload:
        print('request: ',json.dumps(payload))
    r = requests.post(url,json=payload)
    return parseResponse(r,printResult)



