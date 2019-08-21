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
    locator = (By.XPATH, "//div[@id='pages']/span")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    locator = (By.XPATH, "//div[@id='ajaxpage-list']/a[1]")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]

    if int(cnum) != int(num):
        driver.execute_script('ajaxGoPage(%s)'%num)

        locator = (By.XPATH, '//div[@id="ajaxpage-list"]/a[1][not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)

    content_list = body.xpath("//div[@id='ajaxpage-list']/a")

    data = []
    for content in content_list:
        name = content.xpath("./@title")[0].strip()
        url = content.xpath("./@href")[0].strip()
        ggstart_time = content.xpath("./div[2]/text()")[0].strip()

        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='pages']/font/font/font")
    total_page = re.findall('共(\d+)页',WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='main_512 over_hidd']")
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
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='main_512 over_hidd')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "https://www.xjawt.gov.cn/zwgk/czzj/zbgg/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhao_bian_gg",
     "https://www.xjawt.gov.cn/zwgk/czzj/zfcg/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "https://www.xjawt.gov.cn/zwgk/czzj/zbgg2498/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆自治区阿克苏地区阿瓦提县", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_xinjiang_awati"]
    work(conp)

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
    # #
