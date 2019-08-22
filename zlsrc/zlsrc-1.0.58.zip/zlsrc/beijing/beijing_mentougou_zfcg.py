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
from zlsrc.util.fake_useragent import UserAgent
from zlsrc.util.etl import est_html, est_meta, add_info
import time


ua = UserAgent()

headers = {

    'User-Agent': ua.random,
}


def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)
        ip = r.text
        proxy = {'http': ip}
    except:
        proxy = {}
    return proxy


def get_response(driver, url, param_data):
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
    type = driver.current_url.rsplit('#',1)[-1]
    param_data = {
        'type': type,
        'orderByColumn': 'post_date desc',
        'pageNum': num,
        'pageSize': '12',
        'menu': '',
    }
    res = get_response(driver, 'http://zfcg.bjmtg.gov.cn/getMoreBulletin', param_data)
    contents = json.loads(res,encoding='utf8')
    content_list = contents.get("obj").get('list').get("results")
    data = []
    for content in content_list:
        name = content.get("mainTitle")
        orgName = content.get("orgName")

        ggstart_time = datetime.utcfromtimestamp(int(content.get("postDate")/1000)).strftime("%Y-%m-%d")
        info_temp  = {'组织名字':orgName}
        try:
            url = 'http://zfcg.bjmtg.gov.cn' + content.get("contentPath")
        except:
            url = 'None'
            info_temp.update({'hreftype':'不可抓网页'})


        info = json.dumps(info_temp,ensure_ascii=False)

        temp = [name, ggstart_time, url,info]
        data.append(temp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    type = driver.current_url.rsplit('#',1)[-1]
    param_data = {
        'type': type,
        'orderByColumn': 'post_date desc',
        'pageNum': '1',
        'pageSize': '12',
        'menu': '',
    }
    res = get_response(driver, 'http://zfcg.bjmtg.gov.cn/getMoreBulletin', param_data)
    contents = json.loads(res,encoding='utf8')
    total_page = math.ceil(int(contents.get("obj").get('list').get('totalRecord'))/15)

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news']")
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
    div = soup.find('div', class_='news')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#gzgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_dyly_gg",
     "http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#dyly",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_chengjiao_gg",
     "http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#zbcj",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"成交"}), f2],

    ["zfcg_liubiao_gg",
     "http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#fbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_hetong_gg",
     "http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#cght",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_gg",
     "http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#qtgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

###北京市门头沟区财政局
def work(conp, **args):
    est_meta(conp, data=data, diqu="北京市门头沟区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_beijing_mentougou"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get('http://zfcg.bjmtg.gov.cn/moreBulletin/qtgg#')
    # f2(driver)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     df_list = f1(driver, i).values.tolist()
    #     print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
