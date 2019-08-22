import json
import random

import pandas as pd
import re
from urllib import parse
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zlsrc.util.etl import  est_meta, est_html, add_info, est_gg
from zlsrc.util.fake_useragent import UserAgent

ua=UserAgent()

def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}
    url=driver.current_url
    url = parse.unquote(url, encoding='utf8')
    main_url = url.split('$$')[0]
    para = url.split('$$')[1]
    category = re.findall('category:(.+?)/', para)[0]
    type_ = re.findall('/type:(.+)', para)[0]
    headers = {
        "User-Agent": ua.chrome,
        "Referer": "http://60.6.253.156:8888/sszt-zyjyPortal/",
    }

    form_data = {
        "category": category,
        "type": type_,
        "page": num,
        "rows": 8,
    }

    req = requests.post(main_url, data=form_data,proxies=proxies, headers=headers, timeout=20)
    if req.status_code != 200:
        raise ValueError("error response status code %s"%req.status_code)
    data=[]
    res = req.json()
    contents = res['rows']
    for c in contents:
        diqu = c.get('region_Code_Name')
        ggstart_time = c.get('noticeSendTime')
        name = c.get('title')
        href = c.get('id')
        href = "http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/tradeEdit?id=" + str(href)
        info = json.dumps({"diqu": diqu}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}

    url = driver.current_url
    url=parse.unquote(url,encoding='utf8')

    main_url=url.split('$$')[0]
    para=url.split('$$')[1]
    category=re.findall('category:(.+?)/',para)[0]
    type_=re.findall('/type:(.+)',para)[0]
    headers = {
        "User-Agent": ua.chrome,
        "Referer": "http://60.6.253.156:8888/sszt-zyjyPortal/",
    }

    form_data = {
        "category":category,
        "type":type_,
        "page":1,
        "rows":8,
    }

    req = requests.post(main_url, data=form_data, headers=headers, proxies=proxies, timeout=20)
    if req.status_code != 200:
        raise ValueError("error response status code %s" % req.status_code)

    res = req.json()
    total = res['total']
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="show_nav"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='show_containt')

    return div



data=[

["zfcg_zhaobiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:政府采购/type:招标公告', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_biangeng_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:政府采购/type:变更公告', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_zhongbiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:政府采购/type:中标公告', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_liubiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:政府采购/type:废标公告', ["name", "ggstart_time", "href", 'info'],f1, f2],
["zfcg_dyly_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:政府采购/type:公示公告', ["name", "ggstart_time", "href", 'info'],f1, f2],

["gcjs_zhaobiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:建设工程/type:招标公告', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_biangeng_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:建设工程/type:变更公告', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiaohx_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:建设工程/type:中标公示', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:建设工程/type:中标公告', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_liubiao_gg" , 'http://60.6.253.156:8888/sszt-zyjyPortal/zyjyPortal/portal/noticelist$$category:建设工程/type:废标公告', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###邢台市公共资源交易网
def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省邢台市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=False,
        num=1,
        )
    pass
