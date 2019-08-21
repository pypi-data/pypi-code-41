import json
import random
import re

import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time



def f1(driver, num):
    locator = (By.XPATH, '//span[@class="cpb"]')
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    locator = (By.XPATH, "//ul[@class='notices']/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]

    if int(cnum) != int(num):
        new_url = re.sub('pageIndex=\d+','pageIndex='+str(num),driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//ul[@class="notices"]/li[1]/a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)

    content_list = body.xpath("//ul[@class='notices']/li")

    data = []
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://117.149.224.229'+content.xpath("./a/@href")[0].strip()

        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//a[contains(string(),'尾页')]")
    total_page = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href').rsplit('=',1)[-1])
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='content']")
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('div', id='content')
    return div


data = [
    ["gcjs_zhaobiao_sg_gg",
     "http://117.149.224.229/PMNotice/Notice/NoticeList/zbxx/jsgc?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://117.149.224.229/PMNotice/Notice/NoticeList/zhongbxx/jsgc?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省温州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_zhejiang_wenzhou"]
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
    #
