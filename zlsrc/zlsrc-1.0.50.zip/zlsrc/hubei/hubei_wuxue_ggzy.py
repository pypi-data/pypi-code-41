import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import  est_meta, est_html,  add_info



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageNum=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=pageNum=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//div[@class="default_pgContainer"]/table//tr[1]//a').get_attribute('href')[-25:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="default_pgContainer"]/table//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('div', class_='default_pgContainer').find('table').find_all('tr')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',class_="bt_time").get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.wuxue.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = driver.find_element_by_xpath('//span[@class="default_pgTotalPage"]').text
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="zoom"][string-length()>100]')
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

    div = soup.find('div', id="zoom").parent

    if div == None:
        raise ValueError('div is None')

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://ggzy.wuxue.gov.cn/col/col2120/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://ggzy.wuxue.gov.cn/col/col2121/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://ggzy.wuxue.gov.cn/col/col2122/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg", "http://ggzy.wuxue.gov.cn/col/col2123/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://ggzy.wuxue.gov.cn/col/col4029/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ggzy.wuxue.gov.cn/col/col2124/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_da_bian_gg", "http://ggzy.wuxue.gov.cn/col/col2125/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiaohx_gg", "http://ggzy.wuxue.gov.cn/col/col2126/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_dyly_gg", "http://ggzy.wuxue.gov.cn/col/col2127/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://ggzy.wuxue.gov.cn/col/col2128/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://ggzy.wuxue.gov.cn/col/col4030/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg", "http://ggzy.wuxue.gov.cn/col/col2135/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"乡镇交易"}), f2],
    ["jqita_zhongbiao_gg", "http://ggzy.wuxue.gov.cn/col/col2136/index.html?uid=8240&pageNum=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"乡镇交易"}), f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省武穴市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_wuxue"], total=2, headless=False, num=1)



