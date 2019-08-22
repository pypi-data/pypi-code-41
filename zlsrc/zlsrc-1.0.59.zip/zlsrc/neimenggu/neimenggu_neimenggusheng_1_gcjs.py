import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_tbs, est_meta, est_html



def f1(driver, num):
    locator = (By.XPATH, '//li[@class="p14 hui8"][1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if 'index.shtml' in url:
        cnum=1
    else:
        cnum = int(re.findall('index_(\d+)', url)[0])

    if int(cnum) != int(num):
        if num == 1:
            url=re.sub('(?<=index_)\d+','index',url)
        else:
            url=re.sub('index_*\d*.shtml','index_%s.shtml'%num,url)


        val = driver.find_element_by_xpath('//li[@class="p14 hui8"][1]/a').get_attribute('href')[-25:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//li[@class="p14 hui8"][1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find_all('li',class_='p14 hui8')

    for tr in div:

        href=tr.a['href']
        name=tr.a.get_text(strip=True)
        ggstart_time=tr.find('span',class_='r').get_text(strip=True)

        if 'http' in href:
            href = href
        else:
            href = 'http://jtyst.nmg.gov.cn' + href
        tmp = [name, ggstart_time, href]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="p14 hui8"][1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    page = driver.find_element_by_link_text('尾页').get_attribute('href')
    total=re.findall('index_(\d+)',page)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="Zoom"][string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
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

    div = soup.find('div',class_="yyxwxxy_nr")


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://jtyst.nmg.gov.cn/jtzw/gsgg/zbgg/index.shtml",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://jtyst.nmg.gov.cn/jtzw/gsgg/zbgg_1/index.shtml",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="内蒙古自治区", **args)
    est_html(conp, f=f3, **args)


### 内蒙古交通运输厅


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "heshan"], total=2, headless=True, num=1)



