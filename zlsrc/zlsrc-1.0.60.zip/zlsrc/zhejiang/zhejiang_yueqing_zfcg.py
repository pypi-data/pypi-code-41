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

_name_ = 'zhejiang_yueqing_zfcg'


def f1(driver, num):

    driver.get(re.sub('pageNum=\d+', 'pageNum='+str(num) ,driver.current_url))
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='default_pgContainer']/div[position()!=1]")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='default_pgContainer']/div[position()!=1]")
    data = []
    for content in content_list:
        name =  content.xpath('./div/a/@title')[0].strip()
        ggstart_time =  content.xpath('./div[2]/text()')[0].strip()
        href = 'http://www.yueqing.gov.cn'+content.xpath('./div/a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
        #//td[@id='Paging']/table/tbody/tr/td/font[2]/b
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//span[@class='default_pgTotalPage']"))).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='c']")
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
    div = soup.find('table', id='c')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.yueqing.gov.cn/col/col1347879/index.html?uid=4376880&pageNum=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.yueqing.gov.cn/col/col1347882/index.html?uid=4376880&pageNum=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 浙江省乐清市人民政府办公室
def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省乐清市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "zhejiang_yueqing_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30)
