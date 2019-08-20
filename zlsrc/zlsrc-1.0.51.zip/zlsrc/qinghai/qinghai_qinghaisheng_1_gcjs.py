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

_name_ = 'qinghai_qinghaisheng_gcjs'


def f1(driver, num):
    driver.get(re.sub('pi=\d+', 'pi=' + str(num), driver.current_url))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[normalize-space(@class)='article_list']/ul/li")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[normalize-space(@class)='article_list']/ul/li")
    data = []
    for content in content_list:
        name = content.xpath('./a/text()')[0].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip().strip('[]')
        href = 'http://jtyst.qinghai.gov.cn' + content.xpath('./a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_temp = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='pagecss']"))).text
    total_page = re.findall('/(\d+)页', total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="article_content"][string-length()>50]')
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
    div = soup.find('div',class_='article_content')
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://jtyst.qinghai.gov.cn/companynews/zbgg/?pi=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://jtyst.qinghai.gov.cn/companynews/zbgs/?pi=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://jtyst.qinghai.gov.cn/companynews/zbjggs/?pi=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


# 青海交通，青海省交通厅，青海省交通运输厅
def work(conp, **args):
    est_meta(conp, data=data, diqu="青海省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qinghai_qinghaisheng_gcjs"]
    # driver = webdriver.Chrome()
    # driver.get(data[0][1])
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp, total=50, ipNum=5, num=4)
