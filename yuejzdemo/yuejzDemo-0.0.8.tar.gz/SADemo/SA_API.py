import requests
import json

import urllib.request as urllib2

def login():
    data = {"username": "admin",
            "password": "123456"
            }

    # 1qaz2wsx

    url3 = 'https://test-hechun.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong'


    url4 ='https://sdk-test.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong'

    headers = {'Content-Type': 'application/json'}  ## headers中添加上content-type这个参数，指定为json格式
    response = requests.post(url=url4,
                             headers=headers,
                             data=json.dumps(data))  ## post的时候，将data字典形式的参数用json包转换成json格式。
    return response

    # print(response.json())
    # json = json.dumps(response.text)
    # print('\n')
    # print(response.text)


 # __send_request(
 #        url='https://sdk-test.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong'
 #        content={'username': "admin", 'password': "123456"}
 #        headers={'Content-Type': 'application/json'}


def login_format_importer():
    # __send_request(

        # url='https://sdk-test.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong'
        # content={'username': "admin", 'password': "123456"}
        # headers={'Content-Type': 'application/json'}
    # try:
    headers = {'Content-Type': 'application/json'}
    data4 = {"username": "admin",
            "password": "123456"
            }

    data3 = {"username": "admin",
             "password": "1qaz2wsx"
             }

    data = {
        "username": "admin",
        "password": "ca90fa94"
    }
    # 8
    # f4703591d0b7e4c37619656b2d38bc9e5acfc0091e589785114bbd435fe5e41
    url3 = 'https://test-hechun.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong'
    url4 = 'https://sdk-test.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong'
    request = urllib2.Request(url='https://juyanwang.cloud.sensorsdata.cn/api/auth/login?project=production',
                              # data=bytes(json.dumps(data), encoding="utf-8"),
                              data=json.dumps(data).encode(),
                              headers=headers)
    response = urllib2.urlopen(request)
    response_content = json.loads(response.read().decode('utf-8'))
    # print(response.read().decode('utf-8'))
    return response_content



def saapi(token):
    urla = 'https://test-hechun.cloud.sensorsdata.cn/api/events/report?token=' + token + '&project=yuejianzhong'


    print(urla)
    urlb = 'https://test-hechun.cloud.sensorsdata.cn/api/account?token=570cff04c9bc7b802d11abccd2035bb558e8b5ec221943c1e35b10ec269caed0&project=yuejianzhong'


    data2 = {"measures": [{"event_name": "$AppStart", "aggregator": "unique"}], "unit": "day", "sampling_factor": 64,
             "axis_config": {"isNormalize": False, "left": [], "right": []}, "from_date": "2019-03-19",
             "to_date": "2019-03-25", "tType": "n", "ratio": "n", "approx": False, "by_fields": [], "filter": {},
             "detail_and_rollup": True, "request_id": "1553596932966:761148", "use_cache": True}

    headers = {'Content-Type': 'application/json'}  ## headers中添加上content-type这个参数，指定为json格式
    response = requests.post(
        url=urlb,
        headers=headers,
        data=json.dumps(data2))
    return response
    # print(response.json())
    # json = json.dumps(response.text)
    # print(response.status_code)
    # print('\n')
    #
    # print(response.text)

def check_url(url):
    '''
    导入url: http://xxxx:8106/sa?project=xxx
    确认url: http://xxxx:8106/debug
    '''
    debug_url = urllib.urlparse(url)
    ## 将 URI Path 替换成 Debug 模式的 '/debug'
    debug_url = debug_url._replace(path = '/debug')
    logger.debug('debug url: %s' % debug_url.geturl())
    with urllib2.urlopen(debug_url.geturl()) as f:
        response = f.read().decode('utf8').strip()
        if response != 'Sensors Analytics is ready to receive your data!':
            raise Exception('invalid url %s' % url)


def sauser():
    data2 = [{"username":"xiaoedsadwn3dsa@11.com","role":"64","password":"12333@xee"}]

    headers = {'Content-Type': 'application/json'}  ## headers中添加上content-type这个参数，指定为json格式
    response = requests.put(
        url='https://test-hechun.cloud.sensorsdata.cn/api/account?token=570cff04c9bc7b802d11abccd2035bb558e8b5ec221943c1e35b10ec269caed0&project=yuejianzhong',
        headers=headers,
        data=json.dumps(data2))
    return response


def token_death():
    data3 = {"username": "admin",
             "expired_interval": "2"
             }

    headers = {'Content-Type': 'application/json'}  ## headers中添加上content-type这个参数，指定为json格式
    response = requests.post(
        url='https://test-hechun.cloud.sensorsdata.cn/api/auth/login?token=570cff04c9bc7b802d11abccd2035bb558e8b5ec221943c1e35b10ec269caed0&project=yuejianzhong',
        headers=headers,
        data=json.dumps(data3))
    return response.text


if __name__ == '__main__':
    # re = login()
    # print(re.text)
    # j = json.loads(re.text)
    # print(re.text)
    # print('\n')
    # print(type(j))
    # print(j['token'])

    # print('\n')
    # re1 = saapi()
    # print(re1.text)
    # logtoken = login().text
    # loginjson = json.loads(logtoken)
    # print(saapi(j))


    sap = token_death()
    # jsonsa = json.dumps(sap)
    j = json.loads(sap)
    # token=j['token']
    # print(type)
    print(j['token'])
    # lo = sauser()
    # print(lo)

    print(saapi(j['token']).status_code)
