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



_name_ = 'guizhou_liupanshui_shuicheng_zfcg'


def f1(driver, num):
    driver.get(re.sub('index[_\d]+', 'index_' + str(num-1) if num!=1 else 'index' , driver.current_url))
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,"//div[@class='NewsList']/ul/li/a")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='NewsList']/ul/li")
    data = []
    for content in content_list:
        name = content.xpath('./a/@title')[0].strip()
        href = content.xpath('./a/@href')[0].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_page = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//div[@class="page"]/ul/li[last()-1]/a'))).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="body_contenter w1080"]')
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
    div = soup.find('div', class_='body_contenter w1080')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.shuicheng.gov.cn/xxgk/zdlygk/zfcg/zbgg/index_1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.shuicheng.gov.cn/xxgk/zdlygk/zfcg/zbgg_34630/index_1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

# 贵州水城县人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="贵州省六盘水市水城县", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "guizhou_liupanshui_shuicheng_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'https://xxgkapi.cn3x.com.cn/show/lists?jsoncallback=jQuery31109733300098252529_1565062723220&areaid=10&webid=352&cid=44&sid=&page=10&pagenums=20&orderby=0&_=1565062723223')
    # # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp)
