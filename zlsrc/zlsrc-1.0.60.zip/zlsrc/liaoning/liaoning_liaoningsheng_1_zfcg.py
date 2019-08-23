import json

import math
import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.fake_useragent import UserAgent
from zlsrc.util.etl import est_meta, est_html, add_info

ua = UserAgent()

proxy = {}
headers = {

    'User-Agent': ua.random
}

#
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


def get_responst(driver, data):
    driver_info = webdriver.DesiredCapabilities.CHROME
    post_url = 'http://www.ccgp-liaoning.gov.cn/portalindex.do?method=getPubInfoList&t_k=null'
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
        else:
            proxies = {}
        page = requests.post(post_url, data=data, proxies=proxies, headers=headers, timeout=40).text
    except:
        try:
            page = requests.post(post_url, data=data, headers=headers, timeout=40, proxies=proxy).text
        except:
            page = requests.post(post_url, data=data, headers=headers, timeout=40, proxies=proxy).text

    return page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@cellpadding='15']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('table', cellpadding='15')
    return div


def f1(driver, num):
    tag_jump(driver)
    infoTypeCode = driver.execute_script('return params.infoTypeCode')

    data = {
        'current': num,
        'rowCount': '10',
        'searchPhrase': '',
        'infoTypeCode': infoTypeCode,
    }
    page = get_responst(driver, data)
    body = json.loads(page)
    content_list = body.get('rows')
    data = []

    for content in content_list:
        name = content.get('title')
        area = content.get('districtName')
        ggType = content.get('infoTypeName')
        status = content.get('stateName')
        ggstart_time = content.get('tovStart')
        ggend_time = content.get('tovEnd')
        id = content.get('id')

        url = 'http://www.ccgp-liaoning.gov.cn/portalindex.do?method=getPubInfoViewOpen&infoId=' + id

        info = json.dumps({'area': area, 'ggType': ggType, 'status': status, 'ggend_time': ggend_time}, ensure_ascii=False)

        temp = [name, ggstart_time, url, info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)

    return df


def tag_jump(driver):
    tag = driver.current_url.split('#')[-1]
    js = tag_dict[tag]
    driver.execute_script(js)


def f2(driver):
    tag_jump(driver)

    locator = (By.XPATH, '//span[@class="text-default"]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    total_item = int(re.findall('共 (\d+) 条', txt)[0])
    total_page = math.ceil(total_item / 10)

    driver.quit()
    return int(total_page)


tag_dict = {
    "cggg": 'queryall(SYLM.CGGG)',
    "dyly": 'queryall(SYLM.DYLYGG)',
    "jggg": 'queryall(SYLM.JGGG)',
    "zbwj": 'queryall(SYLM.ZBWJGS)',
    "qt": "queryall('QTGG')",
}

data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://www.ccgp-liaoning.gov.cn/portalindex.do?method=goPubInfoList#cggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_dyly_gg",
     "http://www.ccgp-liaoning.gov.cn/portalindex.do?method=goPubInfoList#dyly",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_zhongbiao_gg",
     "http://www.ccgp-liaoning.gov.cn/portalindex.do?method=goPubInfoList#jggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_gqita_gg",
     "http://www.ccgp-liaoning.gov.cn/portalindex.do?method=goPubInfoList#qt",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="辽宁省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    # url = "http://www.ahtba.org.cn/Notice/AnhuiNoticeSearch?spid=714&scid=597&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15"
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver, 2)
    #     for ur in df.values.tolist()[:1]:
    #         print(f3(driver, ur[2]))
    #     driver.get(d[1])
    #     print(f2(driver))

    #
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_liaoning_shenghui"])

    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 3)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
