import json
import random
import re

import math
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time


def f1(driver, num):
    url=driver.current_url
    if num == 1:
        url=re.sub('index[_\d]*.html','index.html',url)
    else:
        url=re.sub('index[_\d]*.html', 'index_%s.html'%(str(num - 1)), driver.current_url)
        # print(url)
    driver.get(url)

    locator = (By.XPATH, '//table[@class="list_bk2"]/tbody/tr/td/table[@width="97%"]/tbody/tr/td/a')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)

    content_list = body.xpath('//table[@class="list_bk2"]/tbody/tr/td/table[@width="97%"]')

    data = []
    for content in content_list:
        name = content.xpath("./tbody/tr/td/a/@title")[0].strip()
        ggstart_time = content.xpath("./tbody/tr/td[3]/text()")[0].strip()
        url = driver.current_url.rsplit('/',1)[0] + content.xpath("./tbody/tr/td/a/@href")[0].strip().strip('.')
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//a[contains(text(),"末页")]')
    text = re.findall('(\d+)',(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')))[0]
    if not text:
        total_page = 1
    else:
        total_page = text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//tr[@valign="top"]')
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('tr', valign='top')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://hfzdj.hefei.gov.cn/ztbxx/zbgg/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://hfzdj.hefei.gov.cn/ztbxx/zbxx/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

###合肥市重点工程建设管理局
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省合肥市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_anhui_hefei"]
    work(conp,num=1)
    # driver= webdriver.Chrome()
    # driver.get('http://hfzdj.hefei.gov.cn/ztbxx/zbxx/index_1.html')
    # f1(driver,4)
    # print(f2(driver))
    # for d in data[-1:]:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     for i in range(1, total, 10):
    #         driver.get(d[1])
    #         print(d[1])
    #         df_list = f1(driver, i).values.tolist()
    #         print(df_list[:10])
    #         df1 = random.choice(df_list)
    #         print(str(f3(driver, df1[2]))[:100])
    #
