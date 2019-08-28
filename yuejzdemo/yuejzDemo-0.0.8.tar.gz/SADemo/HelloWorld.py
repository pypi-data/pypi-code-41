import sensorsanalytics
# print('hello world')
# print(2**10)
# name = input()
# print(name)
#print(10//3)
# sum = 0
# for x in range(101):
#     sum = sum + x
# print(sum)
# a = set([4,5,6])
# print(a)
# a.add((1, 2, 3))
# print(a)


# consumer = sensorsanalytics.LoggingConsumer("/Applications/logagent/data/py/access.log")
# sa = sensorsanalytics.SensorsAnalytics(consumer)
#
#
# sa.track("abc","abc")
# sa.flush()
# def odd():
#     print('step 1')
#     yield 1
#     print('step 2')
#     yield(2)
#     print('step 3')
#     yield(2)
#
# o = odd()
# next(o)
# next(o)
#next(o)

# def count():
#     def f(j):
#         def g():
#             return j*j
#         return g
#     fs = []
#     for i in range(1, 4):
#         fs.append(f(i)) # f(i)立刻被执行，因此i的当前值被传入f()
#     return fs
# f1, f2, f3 = count()
#
# print(f1(),f2(),f3())
#
# def log(func):
#     def wrapper(*args, **kw):
#         print('call %s():' % func.__name__)
#         return func(*args, **kw)
#     return wrapper
#
# @log
# def now():
#     print('2015-3-25')
#
# now()

# def log(text):
#     def decorator(func):
#         def wrapper(*args, **kw):
#             print('%s %s():' % (text, func.__name__))
#             return func(*args, **kw)
#         return wrapper
#     return decorator
#
# @log('execute')
# def now():
#     print('2015-3-25')
#
# now()

# class Student(object):
#     def __init__(self,name):
#         self.name= name
#     def __str__(self):
#         return 'Student object (name: %s)' % self.name
#
#
# print(Student('ac'))
#
# from enum import Enum
#
# class Gender(Enum):
#     male = 0
#     female = 1
#
# class student(object):
#     def __init__(self,name,gender):
#         self.name = name
#         self.gender = gender
#
# bart = student("acb",Gender.male)
#
# if bart.gender == Gender.male:
#     print("yes")
# else:
#     print("no")


# from functools import reduce
# import logging
#
# def str2num(s):
#     if '.' in s:
#         return float(s)
#     else:
#         return int(s)
#
# def calc(exp):
#     try:
#         ss = exp.split('+')
#         ns = map(str2num, ss)
#         return reduce(lambda acc, x: acc + x, ns)
#     except ValueError as e:
#         logging.info(e)
#
#
# def main():
#     r = calc('100 + 200 + 345')
#     print('100 + 200 + 345 =', r)
#     r = calc('99 + 88 + 7.6')
#     print('99 + 88 + 7.6 =', r)
#     r = calc('a + b + c')
#     print('a + b + c =', r)
#
# main()
#

# with open('/Users/yuejz/Downloads/log.txt') as f:
#     for line in f.readlines():
#         print(line.strip())

import os
# print(os.path.abspath('.'))
# os.path.join('/Users/yuejz/pythonSrc/FirstDemo','test')
# os.mkdir('/Users/yuejz/pythonSrc/FirstDemo/test')
# os.rmdir('/Users/yuejz/pythonSrc/FirstDemo/test')
# os.chdir('/Users/yuejz/pythonSrc/FirstDemo')

# for name in os.listdir('/Users/yuejz/pythonSrc/FirstDemo'):
#     print(name)
import os

# import os
# def search_file(dir,sname):
#     if sname in os.path.split(dir)[1]: #检验文件名里是否包含sname
#         print(os.path.relpath(dir)) #打印相对路径，相对指相对于当前路径
#     if os.path.isfile(dir):   # 如果传入的dir直接是一个文件目录 他就没有子目录，就不用再遍历它的子目录了
#         return
#
#     for dire in os.listdir(dir): # 遍历子目录  这里的dire为当前文件名
#         search_file(os.path.join(dir,dire),sname) #jion一下就变成了当前文件的绝对路径
#                                            # 对每个子目录路劲执行同样的操作
#
# def search(filename,dir):
#     for root, dirs, files in os.walk(dir):
#         for name in files:
#             if filename in name:
#                 print(os.path.join(root, name))
#
# # search_file('/Users/yuejz/pythonSrc/FirstDemo','he')
#
# search('init','/Users/yuejz/pythonSrc/FirstDemo')
# import urllib.request
# import urllib
#
# value={"username":"admin","password":"1qaz2wsx"}
# data=urllib.urlencode(value)
# url="https://test-hechun.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong"
# request=urllib.request.Request(url,data)
# RES=urllib2.urlopen(request)
# print(RES.read())
#
# import urllib.request
# import urllib.parse
# data = urllib.parse.urlencode({"username":"admin","password":"1qaz2wsx"})
# data = data.encode('utf-8')
# request = urllib.request.Request("https://test-hechun.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong")
# # adding charset parameter to the Content-Type header.
# request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
# f = urllib.request.urlopen(request, data)
# print(f.read().decode('utf-8'))

import requests
import json

# data = {"username":"admin",
#         "password":"1qaz2wsx"
#         }
#
# headers = {'Content-Type': 'application/json'}    ## headers中添加上content-type这个参数，指定为json格式
# response = requests.post(url='https://test-hechun.cloud.sensorsdata.cn/api/auth/login?project=yuejianzhong',
#                          headers=headers,
#                          data=json.dumps(data))    ## post的时候，将data字典形式的参数用json包转换成json格式。
#
# # print(response.json())
# # json = json.dumps(response.text)
# print('\n')
# print(response.text)

data1 = {
          "users": [
            'a5227c8e9bdd52fe'
          ],
          "from_date": "2019-03-22",
          "to_date": "2019-03-26",
          # // false 表示 users 参数指定的是内部的 user_id，true 表示传入的是 distinct_id
          "distinct_id": True
        }



data2 ={"measures":[{"event_name":"$AppStart","aggregator":"unique"}],"unit":"day","sampling_factor":64,"axis_config":{"isNormalize":False,"left":[],"right":[]},"from_date":"2019-03-19","to_date":"2019-03-25","tType":"n","ratio":"n","approx":False,"by_fields":[],"filter":{},"detail_and_rollup":True,"request_id":"1553596932966:761148","use_cache":True}


url='https://test-hechun.cloud.sensorsdata.cn/api/events/report?token=yx6u1f4cDqVlzuZlcfDddbXFdBGtz4gXcEgBNbGfQvHunZ8joxCtjtciRcQyPKKqyvnkvpsL19Ft7xx7iU3FTLoYo2gEWmrwOjFOsmsNbIFxE28fesibLpmRA6mQLnB5&project=yuejianzhong',

url1='https://test-hechun.cloud.sensorsdata.cn/api/events/report?token=570cff04c9bc7b802d11abccd2035bb558e8b5ec221943c1e35b10ec269caed0&project=yuejianzhong',



headers = {'Content-Type': 'application/json'}    ## headers中添加上content-type这个参数，指定为json格式
response = requests.post(url='https://test-hechun.cloud.sensorsdata.cn/api/events/report?token=570cff04c9bc7b802d11abccd2035bb558e8b5ec221943c1e35b10ec269caed0&project=yuejianzhong',
                         headers=headers,
                         data=json.dumps(data2))

# print(response.json())
# json = json.dumps(response.text)
print(response.status_code)
print('\n')

print(response.text)

customer_name = 'admin'
sa_site = 'https://test-hechun.cloud.sensorsdata.cn/'
sa_project = 'yuejianzhong'
sa_cookie = 'sensorsdata-token-flag=flag; sa_jssdk_2015_sensors-cms=%7B%22distinct_id%22%3A%22haofenqistandalone%3A19%22%2C%22props%22%3A%7B%22customer_id%22%3A%22haofenqistandalone%22%2C%22project_name%22%3A%22default%22%2C%22username%22%3A%22admin%22%2C%22isDemo%22%3Afalse%2C%22version1%22%3A%221.13%22%2C%22version2%22%3A%221.13.5207%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; sensorsdata2015jssdkcross=%7B%22%24device_id%22%3A%22169717fd0afe6-064ebcf4af2e5a-42554133-2073600-169717fd0b01c9%22%7D; csrftoken=DaAc1I2WQ7c126XASW5sq2MS68rsev9n; api_server_id=qbWbSd1c; sensorsdata-token_default=570cff04c9bc7b802d11abccd2035bb558e8b5ec221943c1e35b10ec269caed0'
event_file_name = '事件设计.xlsx'

# df_raw = pd.read_excel(event_file_name, sheet_name='事件表', header=None)
# df_raw_user = pd.read_excel(event_file_name, sheet_name='用户表', header=None)
# df1 = fetch_track_cols(df_raw)



def obtain_events(site, cookie, project_name):
    print('进入读取神策环境中的事件&属性信息...')
    api_site = site + '/api/events/all'
    # results = requests.get(api_site, params={'project': project_name}, headers={'Cookie': cookie}).text

    results = requests.get(api_site, params={'project': project_name}).text


    if 'error' in results:
        print('请求神策 API 参数错误: 请确认地址、项目名称及 Cookie 是否准确')
        return None
    print(results)
    df = pd.read_json(results)
    df_result_list = []

    for index, item in df.iterrows():
        initial_property_num = 0
        # 去除虚拟事件的检查
        if item['virtual']:
            continue
        api_url = site + '/api/event/{}/properties'.format(item['id'])
        properties = requests.get(api_url, params={'project': project_name}, headers={'Cookie': cookie}).json()['event']

        tmp = []
        for property in properties:
            # 去除带 $ 符号的预置属性，计算通用预置属性的个数
            if property['name'][0] == '$' and property['name'] not in not_initial_property:
                initial_property_num += 1
                continue
            tmp_list = [property['event_name'], item['cname'], property['name'], property['cname'],
                        property['data_type']]
            tmp.append(tmp_list)

        for value in tmp:
            value.append(initial_property_num)
        df_result_list += tmp

    df_result = pd.DataFrame(df_result_list, columns=['event_en', 'event_cn', 'property_en', 'property_cn', 'data_type',
                                                      'initial_p_num'])
    df_result.replace(['string', 'number', 'bool', 'datetime', 'date', 'list'],
                      ['字符串', '数值', 'BOOL', '时间', '日期', '列表'], inplace=True)

    print('神策分析环境中数据信息已获取...')
    return df_result


df_sa = obtain_events(sa_site, sa_cookie, sa_project)
# import sensorsanalytics
#
# # 神策分析数据接收的 URL
# SA_SERVER_URL = 'https://test-hechun.datasink.sensorsdata.cn/sa?project=yuejianzhong&token=d28b875ed9ac268f'
#     # 发送数据的超时时间，单位毫秒
# SA_REQUEST_TIMEOUT = 100000
#     # Debug 模式下，是否将数据导入神策分析
#     #   True - 校验数据，并将数据导入到神策分析中
#     #   False - 校验数据，但不进行数据导入
# SA_DEBUG_WRITE_DATA = True
#
#     # 初始化 Debug Consumer
# consumer = sensorsanalytics.DebugConsumer(SA_SERVER_URL, SA_DEBUG_WRITE_DATA, SA_REQUEST_TIMEOUT)
#
# # 初始化 Logging Consumer
# #consumer = sensorsanalytics.LoggingConsumer('/Applications/logagent/data/py.log')
#
# # consumer = sensorsanalytics.LoggingConsumer('/Applications/logagent/data/py.log')
#
# # 使用 Consumer 来构造 SensorsAnalytics 对象
# sa = sensorsanalytics.SensorsAnalytics(consumer)
# properties = {
#         # 用户性别属性（Sex）为男性
#         '$time' : 1553487334,
#         # 用户等级属性（Level）为 VIP
#         'UserLevel' : 'Elite VIP',
#     }
#
#
# # print(properties['time'])
#
# sa.track(distinct_id="acn",
#          event_name="test",
#          properties=properties,
#          is_login_id=False)
# sa.flush()
# import os
#
# print(os.name)
