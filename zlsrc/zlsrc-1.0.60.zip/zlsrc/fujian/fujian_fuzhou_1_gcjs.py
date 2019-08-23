import json
import random
import re
from datetime import datetime, timedelta
import urllib
import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time

from zlsrc.util.fake_useragent import UserAgent

_name_ = 'fujian_fuzhou_gcjs'

ua = UserAgent()

headers = {

    'Content-Type': 'text/plain',
    'User-Agent': ua.random

}
param = {
    "page": {
        "pageSize": 10,
        "currentPage": 1
    },
    "modelObj": {

    },
    "queryCondition": {
        "tmBidSectionQueryObj": {
            "modelObj": {
                "categoryId": "10001010101"
            }
        },
        "needQueryJoin__tmBidSectionQueryObj": 'true',
        "seqId__notin": " select a.seq_id from TM_SEC_TENDER a where a.section_name like '%测试%'"
    },
    "orderByStr": " update_time desc"
}


def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)
        ip = r.text
        if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
            raise ValueError('[Error]:获取 IP ')
        proxy = {'http': ip}
    except:
        proxy = {}
    return proxy


def get_response(driver, url, param_data, headers):
    proxy = {}
    driver_info = webdriver.DesiredCapabilities.CHROME
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
            page = requests.post(url, data=param_data, proxies=proxies, headers=headers, timeout=50).text
        else:
            if proxy == {}: get_ip()
            page = requests.post(url, data=param_data, headers=headers, timeout=50, proxies=proxy).text
    except:
        try:
            page = requests.post(url, data=param_data, headers=headers, timeout=50, proxies=proxy).text
        except:
            get_ip()
            page = requests.post(url, data=param_data, headers=headers, timeout=50, proxies=proxy).text

    return page


def f1(driver, num):
    headers1 = headers.copy()
    url, categorySelect = driver.current_url.split('#')
    data_param = param.copy()
    data_param['page']['currentPage'] = num
    if categorySelect == '':
        data_param.update({'queryCondition': {"seqId__notin": " select a.seq_id from TM_SEC_TENDER a where a.section_name like '%测试%'"}})
    else:
        data_param["queryCondition"]["tmBidSectionQueryObj"]["modelObj"]["categoryId"] = categorySelect

    data_param_encode = urllib.parse.quote(str(data_param))
    res = get_response(driver, url, data_param_encode, headers1)
    page = json.loads(res)
    content_list = page.get('content')

    data = []
    for content in content_list:
        _ID = content.get('_ID')

        name = content.get('modelObj').get('sectionName')

        ggstart_time = datetime.fromtimestamp(float(content.get('modelObj').get('createTime')) / 1000).strftime('%Y-%m-%d')
        xiangmu_code = content.get('modelObj').get('bidNumber')
        tendereeName = content.get('modelObj').get('tendereeName')
        if 'candidateInfo' in driver.current_url or 'failedInfo' in driver.current_url:
            agentName = content.get('tmBidSectionVoObj').get('modelObj').get('agentName')

        else :
            agentName = content.get('modelObj').get('agentName')

        secId = content.get('modelObj').get('sectionIds')
        page_html = content.get('modelObj').get('tenderContent')
        href = 'http://202.109.197.133:25000/CmsPortalWeb/main/queryProcess.xhtml?secId=' + str(secId) + '&seqId=' + str(_ID)
        info = json.dumps({
            "agentName": agentName,
            "xiangmu_code": xiangmu_code,
            'tendereeName': tendereeName,
            "page_html": page_html
        }, ensure_ascii=False)
        temp = [name, ggstart_time, href, info]
        print(temp)

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    headers1 = headers.copy()
    url, categorySelect = driver.current_url.split('#')
    data_param = param.copy()
    if categorySelect == '':
        data_param.update({'queryCondition': {"seqId__notin": " select a.seq_id from TM_SEC_TENDER a where a.section_name like '%测试%'"}})
    else:
        data_param["queryCondition"]["tmBidSectionQueryObj"]["modelObj"]["categoryId"] = categorySelect
    data_param_encode = urllib.parse.quote(str(data_param))
    res = get_response(driver, url, data_param_encode, headers1).replace('\'', '\"')
    page = json.loads(res)
    totalitems = page.get('page').get('totalItems')
    total_page = math.ceil(int(totalitems) / 10)

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="container main mt-20"][string-length()>50]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='container main mt-20')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://202.109.197.133:25000/CmsPortalWeb/CmsMainData/tenderInfo.xhtml#10001010101",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://202.109.197.133:25000/CmsPortalWeb/CmsMainData/candidateInfo.xhtml#",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://202.109.197.133:25000/CmsPortalWeb/CmsMainData/failedInfo.xhtml#",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


# 福州市公共资源交易服务中心
def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省福州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "fujian_fuzhou_gcjs"]
    work(conp, total=10, ipNum=0, num=1)
    # driver = webdriver.Chrome()
    # driver.get(data[0][1])
    # f1(driver, 9)
    # f1(driver, 1)
