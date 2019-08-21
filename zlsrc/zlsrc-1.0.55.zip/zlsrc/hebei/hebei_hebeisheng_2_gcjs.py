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
    locator = (By.XPATH, '//span[@id="pager_pages"]')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)\/', txt)[0]
    page_title = driver.find_element_by_xpath('//div[@id="mianbaoxie"]').text
    if '招标公告' in page_title:
        mark = 24
    else:
        mark = 25
    locator = (By.XPATH, '//ul[@id="newslist"]/li[1]/div/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-60:]

    if int(cnum) != int(num):
        driver.execute_script('getTender(%s,%s)'%(mark, num))

        try:
            locator = (By.XPATH, '//ul[@id="newslist"]/li[1]/div/a[not(contains(@href,"%s"))]'%val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            locator = (By.XPATH, '//ul[@id="newslist"]/li[2]/div/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@id="newslist"]/li')
    data = []
    for c in content_list:

        name = c.xpath('./div/a/text()')[0].strip()
        url = 'http://www.hbeba.com' + c.xpath('./div/a/@href')[0].strip()

        ggstart_time = c.xpath('./div[2]/text()')[0].strip()

        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@id="pager_pages"]')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)', txt)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="xl_column"][string-length()>150]|//div[@id="newcont"][string-length()>150]')
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
    div = soup.find('div', class_='xl_column')
    if not div:
        div = soup.find('div', id='newcont')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.hbeba.com/Client/liebiao/List.aspx?flag=Tender",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.hbeba.com/Client/liebiao/List.aspx?flag=WinTender",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

##河北省建设工程招标投标协会
def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_hbeba_com"]
    driver = webdriver.Chrome()
    #
    # driver.get('http://www.hbeba.com/Client/liebiao/List.aspx?flag=Tender')
    # print(f2(driver))
    # f1(driver, 1)
    # f1(driver, 5)
    # work(conp, )
    print(f3(driver, 'http://www.hbeba.com/Client/liebiao/Details.aspx?flag=WinTender&id=a93b6d6c-cfa5-4926-9059-599b528b4f21'))
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
