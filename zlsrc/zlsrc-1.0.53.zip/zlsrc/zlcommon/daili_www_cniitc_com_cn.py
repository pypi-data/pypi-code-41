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

###  http://www.cniitc.com.cn/Page/368/MoreModuleID/888/article888/6/default.aspx   #第6页
###  http://www.cniitc.com.cn/Page/368/MoreModuleID/888/article888/8/default.aspx   #第8页

def f1(driver, num):
    new_url = re.sub('article888/\d+', 'article888/' + str(num), driver.current_url)
    driver.get(new_url)
    locator = (By.XPATH, "//div[contains(@id,'Content-')]/div/table/tbody/tr/td/div/div")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[contains(@id,'Content-')]/div/table/tbody/tr/td/div")
    for content in content_list:
        name = content.xpath("./div[1]/a/text()")[0].strip()
        ggstart_time = content.xpath("./div[2]/text()")[0].strip()
        url = 'http://www.cniitc.com.cn' + content.xpath("./div/a/@href")[0].strip()
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
    locator = (By.XPATH, "//div[@id='zhd_ctr1021_ModuleContent']")
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
    div = soup.find('div', id="zhd_ctr1021_ModuleContent")
    return div

data = [
     ["jqita_zhaobiao_gg",
     "http://www.cniitc.com.cn/Page/368/MoreModuleID/888/article888/8/default.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.cniitc.com.cn/Page/370/MoreModuleID/922/article922/1/default.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

####  中仪国际招标公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="中仪国际招标公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "cj", "qycg_www_cniitc_com_cn"]
    work(conp)
    #
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







