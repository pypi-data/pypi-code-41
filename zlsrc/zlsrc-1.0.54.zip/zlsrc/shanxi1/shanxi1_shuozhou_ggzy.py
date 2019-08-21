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

_name_ = 'shanxi1_shuozhou_ggzy'


def f1(driver, num):
    driver.get(re.sub('page=\d+', 'page=' + str(num), driver.current_url))
    page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//body'))).text
    content_list = json.loads(page).get('obj')
    data = []
    for content in content_list:
        name = content.get('PROJECTNAME')
        href = 'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getNoticeDetail&url=' + content.get('URL') + '&id=' + content.get('ID') if 'Result' not in driver.current_url else 'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getResultNoticeDetail&url='+ content.get('URL') + '&id=' + content.get('ID')
        ggstart_time = content.get('RECEIVETIME')
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//body'))).text
    total_items = json.loads(page).get('attribute')
    total_page = math.ceil(int(total_items) / 20)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="class2_body"]')
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
    div = soup.find('div', class_='class2_body')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreResultNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

# 朔州市公共资源交易中心
def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省朔州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "shanxi1_shuozhou_ggzy"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp)
