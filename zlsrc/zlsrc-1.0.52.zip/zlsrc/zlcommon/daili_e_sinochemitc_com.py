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

_name_ = 'qycg_e_sinochemitc_com'



def f1(driver, num):
    driver.get(re.sub('pageNo=\d+', 'pageNo=' + str(num), driver.current_url))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//ul[@class="search-list"]/li')))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="search-list"]/li')
    data = []
    for content in content_list:
        name = content.xpath('./a/@title')[0].strip()
        href = 'http://e.sinochemitc.com' + content.xpath('./a/@href')[0].strip()
        ggstart_time = content.xpath('./p/text()')[0].strip().split(' ')[0]
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pag-link"]/a[last()-2]'))).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="articleMain"]')
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
    div = soup.find('div', class_='articleMain')
    return div


data = [
    ["jqita_gqita_zhao_yu_bian_gg",
     "http://e.sinochemitc.com/cms/channel/ywgg1qb/index.htm?pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://e.sinochemitc.com/cms/channel/ywgg2qb/index.htm?pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_feizhaobiao_gg",
     "http://e.sinochemitc.com/cms/channel/ywgg3qb/index.htm?pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

# 中化招标电子招投标平台
def work(conp, **args):
    est_meta(conp, data=data, diqu="中化商务有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qycg_e_sinochemitc_com"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp)
