from urllib import request,parse
from urllib.request import urlopen

# API 参数配置部分
## 神策分析后台页面访问地址
WEB_URL = 'https://test-hechun.cloud.sensorsdata.cn'
#API Secret，使用 admin 账号获取
API_SECRET = '647f0d77ee1b835a57f4d7d8ab7cb6c24f8b1c2aafbff68bf61efdc365c27e09'
## 项目名称
PROJECT = 'liuwanwan'
## 存放 SQL 语句的文件名
SQL_FILE_NAME = "/Users/liuwanwan/Desktop/test.sql"
## 输出文件名
OUTPUT_FILE_NAME = "/Users/liuwanwan/Desktop/SA_OUTPUT.csv"
## 获取需执行的 SQL 语句
with open(SQL_FILE_NAME,'r') as f:
    SQL_QUERY = "".join(f.readlines())

print("您输入的查询 SQL :\n",SQL_QUERY)
# 拼接 API URL
API_URL = WEB_URL + '/api/sql/query' + '?token=' + API_SECRET + '&project=' + PROJECT
# 配置 API 参数
API_PARAMETERS = {'q':SQL_QUERY,'format':'csv'}
# 提交类型不能为str，需要为byte类型
DATA = parse.urlencode(API_PARAMETERS).encode('utf-8')
# 发起 API 查询请求
REQUEST = request.Request(API_URL, DATA)
# 获取 API 查询结果
RESPONSE = urlopen(REQUEST)
# 将查询结果输出到文件
with open(OUTPUT_FILE_NAME,'w') as f:
    f.write(RESPONSE.read().decode())

print("查询结果已写入 {0} 文件中。".format(OUTPUT_FILE_NAME))