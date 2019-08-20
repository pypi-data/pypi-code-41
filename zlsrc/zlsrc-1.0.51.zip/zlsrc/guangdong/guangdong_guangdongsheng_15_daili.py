import json
import random
import re
from datetime import datetime

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
from zlest1.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'www_zztender_com'


def f1(driver, num):

    driver.get(re.sub('page=\d+', 'page=' + str(num), driver.current_url))
    locator = (By.XPATH, "//ul[@class='list swiper-slide']/a[string-length()>20]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = BeautifulSoup(page, 'html.parser')
    content_list = body.find('ul',class_='list swiper-slide')
    contents = content_list.find_all('a')
    data = []

    for c in contents:
        name = c['title']
        href = c['href']
        ggstart_time =c.find('li').find_all('span')[-1].text
        temp = [name, ggstart_time, href]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@class='pageinfo']")
    href_temp = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)',href_temp)[0]
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="xwnr"]')
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
    div = soup.find('div', class_='xwnr')
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.zztender.com/tender/5bf4e003ebfca/?&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_biangeng_gg",
     "http://www.zztender.com/tender/5bf4e00b9145e/?&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_zhongbiaohx_yucai_gg",
     "http://www.zztender.com/tender/5bf4e01149935/?&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_zhongbiaohx_liu_gg",
     "http://www.zztender.com/tender/5bf4e018dfd40/?&page=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 广东志正招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_zztender_com"]
    # driver = webdriver.Chrome()
    # driver.get('http://www.zztender.com/tender/5bf4e003ebfca/?&page=2')
    # print(f2(driver))

    # f1(driver, 1)
    work(conp)
