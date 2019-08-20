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
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'news_sztc_com'


def f1(driver, num):

    driver.get(re.sub('index[_\d]*', 'index_' + str(num), driver.current_url))
    locator = (By.XPATH, "//body/div[@id='main'][string-length()>30]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = BeautifulSoup(page, 'html.parser')
    content_list = body.find('div',class_='lb-link')
    contents = content_list.find_all('li')
    data = []

    for c in contents:
        name = c.find('span').text
        href = c.a['href']
        ggstart_time =c.find_all('span')[1].text
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pagination']/div/div/a[last()]")
    href_temp = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
    total_page = re.findall('\d+',href_temp)[0]
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="m-bd"]')
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
    div = soup.find('div', class_='m-bd')
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.sztc.com/bidBulletin/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zgys_gg",
     "http://www.sztc.com/preBulletin/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_biangeng_gg",
     "http://www.sztc.com/changeBulletin/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_zhong_zhonghx_gg",
     "http://www.sztc.com/preBidBulletin/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_yucai_gg",
     "http://www.sztc.com/purchaseNotice/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_dazong_gg",
     "http://www.sztc.com/bulkmaterialBulletin/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

#深圳市国际招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qycg_news_sztc_com"]
    # driver = webdriver.Chrome()

    # driver.get('http://www.sztc.com/bulkmaterialBulletin/index_2.htm')
    # print(f2(driver))
    # f1(driver, 1)
    work(conp)
