import json
import random
import re
from datetime import datetime

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

_name_ = 'chongqing_chongqing_nanchuan_zfcg'

ua = UserAgent()

headers = {

    'User-Agent': ua.random,
}


param = {

    'page': '1',
'OrganizationCode': '',
'SubjectCategoryCode': '',
'ThemeCategoryCode': '216,863',
'CustomerCategoryCode': '',
'max': '20',

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


def get_response(driver,url, param_data):
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
    url, code = driver.current_url.split('#')
    param.update({'ThemeCategoryCode':code,"page":num})
    text = get_response(driver,url, param)
    content_list = json.loads(text).get('datalist')
    data = []
    for content in content_list:
        name = content.get('Title')
        href = 'http://zwgk.cqnc.gov.cn'+content.get('Url')
        ggstart_time = content.get('Date')
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    url, code = driver.current_url.split('#')
    param.update({'ThemeCategoryCode':code})
    text = get_response(driver,url, param)
    total_temp  = int(json.loads(text).get('total'))
    total_page = math.ceil(total_temp/20)
    # driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="container02"]')
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
    div = soup.find('div', id='container02')
    return div


data = [
    ["jqita_zhongbiao_gg",
     "http://zwgk.cqnc.gov.cn/zfxx/data/getdata.asp#865",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg",
     "http://zwgk.cqnc.gov.cn/zfxx/data/getdata.asp#216,863",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 重庆市南川区人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市南川区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "chongqing_chongqing_nanchuan_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://zwgk.cqnc.gov.cn/zfxx/data/getdata.asp#865')
    # # print(f2(driver))
    # #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp)
