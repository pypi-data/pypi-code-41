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
    locator = (By.XPATH, '//li[@class="clearfix"][1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=Paging=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//li[@class="clearfix"][1]/a').get_attribute('href')[-40:-20]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//li[@class="clearfix"][1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('li', class_='clearfix')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span',class_="r").get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://yc.xgsggzy.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="clearfix"][1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//td[@class="huifont"]').text
        total = re.findall('/(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//td[@class="infodetail"][string-length()>50]')
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

    div = soup.find('table', id="tblInfo")

    if div == None:
        raise ValueError('div is None')

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004001/004001001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004001/004001002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004001/004001003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004001/004001004/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004001/004001005/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004002/004002001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004002/004002002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://yc.xgsggzy.com/ycweb/jyxx/004002/004002003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],



]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省应城市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_yingcheng"], total=2, headless=False, num=1)



