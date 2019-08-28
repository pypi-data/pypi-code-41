import requests
import json
from urllib import request,parse

WEB_URL = 'https://test-hechun.cloud.sensorsdata.cn'
#API Secret，使用 admin 账号获取
#API_SECRET = '647f0d77ee1b835a57f4d7d8ab7cb6c24f8b1c2aafbff68bf61efdc365c27e09'
## 项目名称
PROJECT = 'liuwanwan'

def login():
    data = {"username": "admin",
            "password": "1qaz2wsx"
            }

    headers = {'Content-Type': 'application/json'}  ## headers中添加上content-type这个参数，指定为json格式
    API_URL = WEB_URL + '/api/auth/login?project=' + PROJECT

    response = requests.post(API_URL,
                             headers=headers,
                             data=json.dumps(data))  ## post的时候，将data字典形式的参数用json包转换成json格式。
    return response

def apitest():
    re = login()
    j = json.loads(re.text)
    print(re.text)
    token = j['token']
    data = {
          "measures": [
            {
              "event_name": "$pageview",
              "aggregator": "unique"
            }
          ],
          "unit": "day",
          "by_fields": [
            "user.$utm_source"
          ],
          "sampling_factor": 64,
          "from_date": "2018-05-01",
          "to_date": "2018-05-31",
          "filter": {

          },
          "request_id": "1556262168986:814358",
        }
    headers = {'Content-Type': 'application/json', 'sensorsdata-token': token}  ## headers中添加上content-type这个参数，指定为json格式
    SQL_URL= WEB_URL + '/api/events/report?project=' + PROJECT

    response = requests.post(SQL_URL,
                             headers=headers,
                             data=json.dumps(data))  ## post的时候，将data字典形式的参数用json包转换成json格式。
    #print(response)
    return response

def sqltest():
    re = login()
    j = json.loads(re.text)
    print(re.text)
    token = j['token']
    SQL_QUERY ='select first_id from users limit 10'
    API_PARAMETERS = {'q':SQL_QUERY,'format':'csv'}

    headers = {'sensorsdata-token': token}  ## headers中添加上content-type这个参数，指定为json格式
    SQL_URL = WEB_URL + '/api/sql/query?project=' + PROJECT +'&q=' + SQL_QUERY + '&format=csv'
    print(SQL_URL)
    response = requests.post(SQL_URL,
                             headers=headers)
                             # data = parse.urlencode(API_PARAMETERS).encode('utf-8')) ## post的时候，将data字典形式的参数用json包转换成json格式。
    # print(response)
    return response

if __name__ == '__main__':
    #tet = apitest()
    sqltxt =sqltest()
    #print(tet.text)
    print(sqltxt.status_code)
    print(sqltxt.text)
    # print(type(j))
    # print(j['token'])
    # j = json.loads(re.text)
    # token=j['token']
    #print(t)

    #print(response.json())
    #jsont = json.dumps(response.text)
    # print('\n')
     # print(response.text)