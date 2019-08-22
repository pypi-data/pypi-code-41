import json
import math

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@width="90%"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('table', width="90%")

    return div


def f1(driver, num):
    locator = (By.XPATH, '//table[@width="100%" and @cellpadding="0"]/tbody/tr[child::td][1]/td/a[2]')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-5:]
    locator = (By.XPATH, '//font[@color="FF0000"]')
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    if int(cnum) != int(num):
        url = re.sub('page=\d+','page='+str(num),driver.current_url)
        driver.get(url)

        locator = (By.XPATH, '//table[@width="100%%" and @cellpadding="0"]/tbody/tr[child::td][1]/td/a[2][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@width="100%" and @cellpadding="0"]/tbody/tr[child::td]')
    for content in content_list:
        temp = content.xpath("./td/a[2]/@title")[0].strip()
        name = re.findall("文章标题：(.*?)\s",temp)[0]
        ggstart_time = re.findall("\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}",temp)[0]
        url = 'http://www.bdzb.com.cn' + content.xpath("./td/a[2]/@href")[0].strip()
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="show_page"]/b[1]')
    txt = int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text)
    total_page = math.ceil(txt/20)
    driver.quit()
    return int(total_page)


data = [
    #
    ["gcjs_zhaobiao_gc_gg",
     "http://www.bdzb.com.cn/Article/ShowClass.asp?ClassID=14&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhaobiao_hw_gg",
     "http://www.bdzb.com.cn/Article/ShowClass.asp?ClassID=15&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhaobiao_fw_gg",
     "http://www.bdzb.com.cn/Article/ShowClass.asp?ClassID=16&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg",
     "http://www.bdzb.com.cn/Article/ShowClass.asp?ClassID=20&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="湖北省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    for d in data:

        driver = webdriver.Chrome()
        url = d[1]
        driver.get(url)
        df = f1(driver, 2)
        #
        for u in df.values.tolist()[:4]:
            print(f3(driver, u[2]))
        driver.get(url)

        print(f2(driver))
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "hubeisheng"])
