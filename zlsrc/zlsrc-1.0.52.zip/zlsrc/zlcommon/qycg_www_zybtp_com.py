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

from zlsrc.util.etl import est_html, est_meta, add_info
import time




def f1(driver, num):

    locator = (By.XPATH, '//option[@selected="selected"]')
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, '//div[@class="List3 Top18"]/ul/li[not(@class) or @class=""][1]/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]

    if int(cnum) != int(num):
        new_url = re.sub('index[_\d]*','index_'+str(num),driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//div[@class="List3 Top18"]/ul/li[not(@class) or @class=""][1]/a[not(contains(@href,"%s"))]'%(val))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="List3 Top18"]/ul/li[not(@class) or @class=""]')

    data = []
    for content in content_list:

        ggstart_time = content.xpath("./span[1]/text()")[0].strip()
        try:
            status = content.xpath("./span[3]/text()")[0].strip()
        except:status = ''
        try:
            name = content.xpath("./a/@title")[0].strip()
        except:name = content.xpath("./a/text()")[0].strip()

        url =  content.xpath("./a/@href")[0].strip()

        info = json.dumps({"status":status},ensure_ascii=False)

        temp = [name, ggstart_time, url,info]
        data.append(temp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):

    locator = (By.XPATH, "//select/option[last()]")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='W1200 Center Top18 shadow5 WhiteBg']")
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
    div=soup.find('div',class_='W1200 Center Top18 shadow5 WhiteBg')
    return div


data = [
    ["qycg_zhaobiao_gc_gg",
     "http://www.zybtp.com/gcggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiaohx_gc_gg",
     "http://www.zybtp.com/gpsgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_gc_gg",
     "http://www.zybtp.com/gjggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhaobiao_hw_gg",
     "http://www.zybtp.com/hcggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiaohx_hw_gg",
     "http://www.zybtp.com/hpsgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_hw_gg",
     "http://www.zybtp.com/hjggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhaobiao_fw_gg",
     "http://www.zybtp.com/fcggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiaohx_fw_gg",
     "http://www.zybtp.com/fpsgs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_fw_gg",
     "http://www.zybtp.com/fjggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]




def work(conp, **args):
    est_meta(conp, data=data, diqu="中原招标采购交易平台", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_zybtp_com"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get('http://zfcg.czt.fujian.gov.cn/3500/noticelist/e8d2cd51915e4c338dc1c6ee2f02b127/?zone_code=350100&zone_name=%E7%A6%8F%E5%B7%9E%E5%B8%82')
    # print(f2(driver))
    # f1(driver,32)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     df_list = f1(driver, i).values.tolist()
    #     print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
