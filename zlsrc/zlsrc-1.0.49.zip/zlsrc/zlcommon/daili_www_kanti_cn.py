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

# http://www.kanti.cn/article/listitem?CategoryID=2&page=0   #第一页
# http://www.kanti.cn/article/listitem?CategoryID=2&page=1   #第二页

def f1(driver, num):
    new_url = re.sub('page=\d+', 'page=' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//ul[@id='cqnews']/li")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@id='cqnews']/li")
    for content in content_list:
        name = content.xpath(".//a/text()")[0].strip()
        ggstart_time = content.xpath(".//span[2]/text()")[0].strip()
        url = 'http://www.kanti.cn' + content.xpath(".//a/@href")[0].strip()
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df




def f2(driver):   # 求总页数
    locator = (By.XPATH,"//div[@class='r_con']/div/table//strong")
    href_temp = WebDriverWait(driver,20).until(EC.presence_of_element_located(locator)).text
    # print(href_temp)
    total_page = href_temp.rsplit('/', 1)[-1]      #把总页数截取出来
    # print(total_page)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='r_con']//tr")
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
    div = soup.find('div', class_="r_con")
    return div

#  http://www.kanti.cn/article/listitem?CategoryID=2&page=1  #招标公告
#  http://www.kanti.cn/article/listitem?CategoryID=4&page=1  #中标公告

data = [
     ["qycg_zhaobiao_gg",
     "http://www.kanti.cn/article/listitem?CategoryID=2&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiao_gg",
     "http://www.kanti.cn/article/listitem?CategoryID=4&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

#####中招康泰招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="中招康泰招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "qycg_www_kanti_cn"]
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
    #         print(11111,i)
    #         df = f1(driver,i)
    #         item_list = df.values.tolist()
    #         # print(f3(driver, item_list[0][2]))
    #         driver.get(d[1])
    #     driver.quit()

    # url = 'http://www.kanti.cn/article/listitem?CategoryID=2&page=2'
    # driver= webdriver.Chrome()
    # driver.get(url)
    # f1(driver,133)

    # url = 'http://www.kanti.cn/article/details?id=1014'
    # driver= webdriver.Chrome()
    # # driver.get(url)
    # # f1(driver,1)
    # print(f3(driver, url))










