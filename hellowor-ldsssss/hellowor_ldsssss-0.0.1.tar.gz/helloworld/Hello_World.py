import requests
def baiducontent():
    c=requests.get('http://www.baidu.com').content.decode('utf8')
    print(c)