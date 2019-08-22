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

_name_ = 'jiangsu_wuxi_gcjs'


def f1(driver, num):

    driver.get(re.sub('index[_\d]+', 'index_'+str(num) if str(num) != str(1) else 'index',driver.current_url))

    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='RightSide_con']/ul/li")))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='RightSide_con']/ul/li")
    data = []
    for content in content_list:
        name =  content.xpath('./a/@title')[0].strip()
        ggstart_time =  content.xpath('./span/text()')[0].strip()
        href = 'http://js.wuxi.gov.cn' + content.xpath('./a/@href')[0].strip()
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    total_page = 20

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='mainCont']")
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
    div = soup.find('div', class_='mainCont')
    return div


data = [
    ["gcjs_gqita_zhao_zhong_gg",
     "http://js.wuxi.gov.cn/zfxxgk/gggs/ztbgggs/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

# 江苏省无锡市城乡建设
def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省无锡市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "jiangsu_wuxi_gcjs"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30)
