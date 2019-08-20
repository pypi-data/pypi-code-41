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



def f1(driver, num):
    # driver.find_element_by_xpath('//a[@id="close_shijiuda"]').click()
    locator = (By.XPATH, '//span[@class="cpb"]')
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//div[@class='main_list']/ul/li[1]/a")
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]

    if int(cnum) != int(num):
        driver.execute_script("__doPostBack('ctl00$ContentPlaceHolder1$AspNetPager1','%s')" % num)
        locator = (By.XPATH, '//div[@class="main_list"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []

    content_list = body.xpath("//div[@class='main_list']/ul/li")
    for con in content_list:
        name = con.xpath('./a/@title')[0].strip()
        url = 'http://ztbzx.hbsjtt.gov.cn' + con.xpath('./a/@href')[0].strip()
        ggstart_time = con.xpath('./span/text()')[0].strip()

        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="ContentPlaceHolder1_AspNetPager1"]/a[last()]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')

    total_page = re.findall('\d+', txt)[-1]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//div[@class="main_list"][string-length()>50]')
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    except:
        if '未将对象引用设置到对象的实例' in driver.page_source:
            return '404'
        else:
            raise TimeoutError
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
    div = soup.find_all('div', class_='main_list')[0]
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ztbzx.hbsjtt.gov.cn/Site/list.aspx?type=gg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://ztbzx.hbsjtt.gov.cn/Site/list.aspx?type=gs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "ztbzx_hbsjtt_gov_cn"]
    # driver = webdriver.Chrome()

    # driver.get('http://ztbzx.hbsjtt.gov.cn/Site/list.aspx?type=gg')
    # f2(driver)
    # f1(driver, 1)
    # f1(driver, 5)
    work(conp, )
    # print(f3(driver, 'http://ztbzx.hbsjtt.gov.cn/Site/details_news.aspx?NewsGuid=I1300000001057866001002&type=gg'))
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     for i in range(1,i):
    #         df_list = f1(driver, i).values.tolist()
        #     print(df_list[:10])
        #     df1 = random.choice(df_list)
        #     print(str(f3(driver, df1[2]))[:100])
        #     driver.quit()
