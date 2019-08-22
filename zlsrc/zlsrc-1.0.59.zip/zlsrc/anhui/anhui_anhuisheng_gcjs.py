import json
import random
import re
import math
import requests
from bs4 import BeautifulSoup
from zlsrc.util.fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta
import time
from selenium import webdriver


ua = UserAgent()

headers = {
'Referer': 'http://www.ahjzx.org.cn/zhongbiaogongshi.aspx',
'User-Agent': ua.random,
}
proxy = {}

# def get_ip():
#     global proxy
#     try:
#         url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
#         r = requests.get(url)
#         time.sleep(1)
#         ip = r.text
#         proxy = {'http': ip}
#     except:
#         proxy = {}
#     return proxy


def get_response(driver, url):
    driver_info = webdriver.DesiredCapabilities.CHROME
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
        else:
            proxies = {}
        page = requests.get(url, proxies=proxies, headers=headers, timeout=50).text
    except:
        try:
            page = requests.get(url, headers=headers, timeout=50, proxies=proxy).text
        except:
            page = requests.get(url, headers=headers, timeout=50, proxies=proxy).text

    return page

def f1(driver, num):
    'http://www.ahjzx.org.cn/IndexHandler.ashx?method=LoadXxfb&cache=655&pageIndex=1&pageSize=15&Xxtype=11&Xxfl=2'
    new_url = re.sub('pageIndex=\d+','pageIndex='+str(num),driver.current_url)
    res = get_response(driver, new_url)
    content_list = json.loads(res).get('rows')

    data = []
    for content in content_list:
        name = content.get("Title")
        Guid = content.get("Guid")
        ggstart_time = content.get("SortId")
        area = content.get("C_Szd")
        Xxtype = content.get("Xxtype")
        Xxfl = content.get("Xxfl")
        Xxly = content.get("Xxly")

        url = 'http://www.ahjzx.org.cn/xiangqingye.aspx?' + 'Type=' + Xxtype + '&aGuid=' + Guid +'&Xxfl=' + Xxfl

        info = json.dumps({'area':area, 'Xxly':Xxly},ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):

    res = get_response(driver,driver.current_url)
    total_page = math.ceil(int(json.loads(res).get('total'))/15)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[contains(@class,"table tab")]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('table', class_=re.compile("table tab"))
    return div


data = [
    ["gcjs_zhongbiao_gg",
     "http://www.ahjzx.org.cn/IndexHandler.ashx?method=LoadXxfb&cache=655&pageIndex=1&pageSize=15&Xxtype=11&Xxfl=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://www.ahjzx.org.cn/IndexHandler.ashx?method=LoadXxfb&cache=392&pageIndex=1&pageSize=15&Xxtype=11&Xxfl=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_anhui_shenghui"]
    work(conp)
