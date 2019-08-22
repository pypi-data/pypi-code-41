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



_name_ = 'qycg_www_kwbid_com_cn'


def f1(driver, num):
    driver.get(re.sub('pageIndex=\d+', 'pageIndex=' + str(num) , driver.current_url))
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,"//ul[@class='snew']/li")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='snew']/li")
    data = []
    for content in content_list:
        name = content.xpath('./a/text()')[0].strip()
        href = 'http://www.kwbid.com.cn' + content.xpath('./a/@href')[0].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_temp = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='diggpager']/a[last()]"))).get_attribute('href')
    total_page = total_temp.rsplit('=',1)[-1]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="sub_acon"]')
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
    div = soup.find('div', id='sub_acon')
    return div



data = [
    ["jqita_zhaobiao_gg",
     "http://www.kwbid.com.cn/News?cabh=02&pageIndex=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "http://www.kwbid.com.cn/News?cabh=03&pageIndex=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.kwbid.com.cn/News?cabh=04&pageIndex=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 广西科文招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qycg_www_kwbid_com_cn"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'https://xxgkapi.cn3x.com.cn/show/lists?jsoncallback=jQuery31109733300098252529_1565062723220&areaid=10&webid=352&cid=44&sid=&page=10&pagenums=20&orderby=0&_=1565062723223')
    # # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp)
