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
from zlsrc.util.etl import est_html, est_meta
import time
from selenium import webdriver

def f1(driver, num):
    new_url = re.sub('curPage=\d+', 'curPage=' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//div[@class='item1']//li")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='item1']//li")
    for content in content_list:
        name = content.xpath('./div/div/a[1]/text()')[0].strip()
        ggstart_time = content.xpath('./div/div[2]/text()')[0].strip()
        url = 'http://www.yncszx.cn' + content.xpath('./div/div/a/@href')[0].strip()
        info_temp = content.xpath("./div[2]/text()")[0].strip()
        xiangmu_code = re.findall('项目编号:(.*)',info_temp)[0]
        endtime = re.findall('截止日期:(.*)',info_temp)[0]
        info = json.dumps({'xiangmu_code':xiangmu_code,'endtime':endtime},ensure_ascii=False)
        temp = [name, ggstart_time, url,info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    total_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//div[@class='pages']/a[last()-1]"))).text
    # print(total_page)
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='item1 clearfix']")
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
    div = soup.find('div', class_='item1 clearfix')
    return div

data = [
    ["jqita_zhaobiao_gg",
     "http://www.yncszx.cn/news/column/tender/tender2?curPage=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bu_gg",
     "http://www.yncszx.cn/news/column/tender/tender3?curPage=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["jqita_zhongbiao_gg",
     "http://www.yncszx.cn/news/column/tender/tender5?curPage=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]
# 云南晨晟招标咨询有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="云南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "jqita_www_yncszx_cn"]
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
    #         df = f1(driver,i)
    #         item_list = df.values.tolist()
    #         # print(f3(driver, item_list[0][2]))
    #         driver.get(d[1])
    #     driver.quit()

    # url = 'http://www.yncszx.cn/news/column/tender/tender2?curPage=1'
    # driver= webdriver.Chrome()
    # driver.get(url)
    # f1(driver,1)
