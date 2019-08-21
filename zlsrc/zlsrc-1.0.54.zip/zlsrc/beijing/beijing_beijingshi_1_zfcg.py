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
from zlsrc.util.etl import est_html, est_meta, add_info
import time




def f1(driver, num):
    locator = (By.XPATH, "//div[@class='f-fl']")
    cnum = int(re.findall('第(\d+)页', WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)[0])


    locator = (By.XPATH, '//div[@class="content-right-content-center"]/li[1]/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-10:]

    if int(cnum) != int(num):
        new_url = re.sub('page=\d+','page='+str(num),driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//div[@class="content-right-content-center"]/li[1]/a[not(contains(@href,"%s"))]'%(val))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="content-right-content-center"]/li')

    data = []
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()

        ggstart_time = content.xpath("./span/text()")[0].strip()

        url = 'http://www.bgpc.gov.cn' + content.xpath("./a/@href")[0].strip()

        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    locator = (By.XPATH, "//div[@class='f-fl']")
    total_page = int(re.findall('共(\d+)页',WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)[0])

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content-right-content']")
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
    div=soup.find('div',class_='content-right-content')
    return div


data = [
    ["qsy_yucai_gg",
     "http://www.bgpc.gov.cn/news/tid/1?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "http://www.bgpc.gov.cn/news/tid/2?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_fzb_gg",
     "http://www.bgpc.gov.cn/news/tid/3?page=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"非招标"}), f2],
    ["qsy_biangeng_gg",
     "http://www.bgpc.gov.cn/news/tid/4?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhongbiao_gg",
     "http://www.bgpc.gov.cn/news/tid/5?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_liubiao_gg",
     "http://www.bgpc.gov.cn/news/tid/6?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]



###北京市政府采购中心
def work(conp, **args):
    est_meta(conp, data=data, diqu="北京市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_beijing_beijing"]
    work(conp,num=1,headless=True,ipNum=0,image_show_gg=2)
    # driver = webdriver.Chrome()
    # driver.get('http://www.gztpc.com/tender/list?pid=4028e68133f22e130133f2a837750000&pageNo=1')
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
