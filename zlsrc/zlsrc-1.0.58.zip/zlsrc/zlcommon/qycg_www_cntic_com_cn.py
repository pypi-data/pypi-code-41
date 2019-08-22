import json
import random
import re
import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from zlsrc.util.fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta,est_meta_large
import time
from selenium import webdriver


##########  http://www.cntic.com.cn/g337/m989/mp7.aspx 第7页

def f1(driver, num):
    new_url = re.sub('mp\d+', 'mp' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//div[@class='xwkx-module-module']//tr/td/div")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='xwkx-module-module']//tr/td/div")
    for content in content_list:
        name = content.xpath("./div[1]/a/text()")[0].strip()
        ggstart_time = content.xpath("./div[2]/text()")[0].strip()
        url = 'http://www.cntic.com.cn' + content.xpath("./div[1]/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):   # 求总页数
    locator = (By.XPATH,"//div[@class='i-pager']/span/span[2]")
    total_page = WebDriverWait(driver,20).until(EC.presence_of_element_located(locator)).text
    # print(total_page)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='dnn_ContentPane']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id="dnn_ContentPane")
    return div

data = [
     ["qycg_zhaobiao_gg",
     "http://www.cntic.com.cn/g337/m989/mp2.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_gg",
     "http://www.cntic.com.cn/g478/m1403/mp4.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

####  中国技术进口集团有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="中国技术进口集团有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "qycg_www_cntic_com_cn"]
    work(conp)

    # for d in data:
    #     # print(d[1])
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     for i in range(1,total,5):
    #         # print(55555,i)
    #         df = f1(driver,i)
    #         item_list = df.values.tolist()
    #         # print(f3(driver, item_list[0][2]))
    #         driver.get(d[1])
    #     driver.quit()







