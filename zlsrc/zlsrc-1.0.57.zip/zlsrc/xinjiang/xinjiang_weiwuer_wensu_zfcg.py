import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info



def f1(driver, num):
    locator = (By.XPATH, '//div[@id="ajaxpage-list"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//div[@id="pages"]/font')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//div[@id="pages"]/span').text

    if int(cnum) != int(num):
        val = driver.find_element_by_xpath('//div[@id="ajaxpage-list"]/a[1]').get_attribute('href')[
              -30:]
        driver.execute_script('ajaxGoPage(%s)' % num)

        # 第二个等待
        locator = (By.XPATH, '//div[@id="ajaxpage-list"]/a[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//div[@id="pages"]/font')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', id='ajaxpage-list')
    lis = div.find_all('a')

    for tr in lis:
        href=tr['href']
        name=tr['title']
        ggstart_time=tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.wszf.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="ajaxpage-list"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@id="pages"]/font')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.find_element_by_xpath('//div[@id="pages"]/font').text
    total = re.findall('共(\d+)页', page)[0]

    driver.quit()
    return int(total)


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

    div = soup.find('div', id='zoom').parent

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["zfcg_zhaobiao_xunjia_gg", "http://www.wszf.gov.cn/zwgk/czzj/cgxx/index.html",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':"询价采购"}), f2],
    ["zfcg_zhaobiao_gg", "http://www.wszf.gov.cn/zwgk/czzj/zbgg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.wszf.gov.cn/zwgk/czzj/zbgg6869/index.html",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省维吾尔自治区温宿县", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "wensuxian"], total=2, headless=True, num=1)



