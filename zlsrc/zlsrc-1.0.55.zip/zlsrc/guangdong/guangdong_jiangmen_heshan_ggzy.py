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
    locator = (By.XPATH, '//div[@class="col-content"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    if 'index.html' in url:
        cnum=1
    else:
        cnum = int(re.findall('index_(\d+)', url)[0])+1

    if int(cnum) != int(num):
        if num == 1:
            url=re.sub('index_\d+','index',url)
        else:
            url=re.sub('index_*\d*.html','index_%s.html'%(num-1),url)

        val = driver.find_element_by_xpath('//div[@class="col-content"]/a[1]').get_attribute('href')[-25:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="col-content"]/a[1][not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div',class_='col-content').find_all('a',recursive=False)

    for tr in div:

        href=tr['href'].strip('.')
        name=tr.find('span',class_='title').get_text(strip=True)
        ggstart_time=tr.find('span',class_='time').get_text(strip=True)

        if 'http' in href:
            href = href
        else:
            href = url.rsplit('/',maxsplit=1)[0] + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="col-content"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    page = driver.find_element_by_xpath('//div[@class="page"]/a[last()]').get_attribute('href')
    total=re.findall('(\d+)',page)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="content"][string-length()>50]')
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

    div = soup.find('div',class_="article")


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["zfcg_zhaobiao_gg", "http://www.heshan.gov.cn/zwgk/ztbxx/zbgg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.heshan.gov.cn/zwgk/ztbxx/zbgg_40567/index.html",["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg", "http://www.heshan.gov.cn/zwgk/ztbxx/jsxmzb/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.heshan.gov.cn/zwgk/ztbxx/jsxmzb_40569/index.html",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省江门市鹤山县", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "heshan"], total=2, headless=True, num=1)



