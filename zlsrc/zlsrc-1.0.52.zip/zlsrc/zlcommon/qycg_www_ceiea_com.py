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
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="listpages"]/b')
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, '//table[@width="640" and @class=""]/tbody/tr/td/a[1]|//table[@width="640" and not(@class)]/tbody/tr/td/a[1]')
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]

    if int(cnum) != int(num):
        new_url = re.sub('_\d+', '_' + str(num), driver.current_url)

        driver.get(new_url)

        locator = (By.XPATH, '//table[@width="640" and @class=""]/tbody/tr/td/a[1][not(contains(@href,"%s"))]|//table[@width="640" and not(@class)]/tbody/tr/td/a[1][not(contains(@href,"%s"))]' % (val,val))
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    a_list = body.xpath('//table[@width="640" and @class=""]/tbody/tr/td/a|//table[@width="640" and not(@class)]/tbody/tr/td/a')
    span_list = body.xpath('//table[@width="640" and @class=""]/tbody/tr/td/span|//table[@width="640" and not(@class)]/tbody/tr/td/span')

    data = []
    for a,span in zip(a_list,span_list):
        name = a.xpath("./text()")[0].strip()
        url = 'http://www.ceiea.com' + a.xpath("./@href")[0].strip()
        ggstart_time = span.xpath("./text()")[0].strip()

        temp = [name, ggstart_time, url]

        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="listpages"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//div[@class="listpages"]/a[last()]').get_attribute('href')
    total = re.findall('_(\d+).htm', total)[0]
    cnum=driver.find_element_by_xpath('//div[@class="listpages"]/b').text


    while int(total) > int(cnum):
        val = driver.find_element_by_xpath('(//a[@class="link8"])[1]').get_attribute(
            'href')[-15:]
        new_url=driver.find_element_by_xpath('//div[@class="listpages"]/a[last()-1]').get_attribute('href')

        driver.get(new_url)
        locator = (By.XPATH, '(//a[@class="link8"])[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
        total = driver.find_element_by_xpath('//div[@class="listpages"]/a[last()]').get_attribute('href')
        total = re.findall('_(\d+).htm', total)[0]
        cnum = driver.find_element_by_xpath('//div[@class="listpages"]/b').text

    total_page = driver.find_element_by_xpath('//div[@class="listpages"]/b').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@class="table2"]')
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
    div = soup.find('table', class_='table2')
    return div


data = [
    ["qycg_zhaobiao_gg",
     "http://www.ceiea.com/stock/0_1.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_gg",
     "http://www.ceiea.com/zbcg/69_1.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国教育装备网", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_ceiea_com"]
    # driver=webdriver.Chrome()
    # driver.get('http://www.ceiea.com/stock/0_11.htm')
    # f2(driver)
    # print(f1(driver, 3).values.tolist())
    work(conp,num=1,headless=False)
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
    #     # print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
