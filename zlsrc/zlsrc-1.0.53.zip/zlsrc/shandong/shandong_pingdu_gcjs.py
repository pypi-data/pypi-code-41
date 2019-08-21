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
from zlsrc.util.etl import est_tbs, est_meta, est_html



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="s-list"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if 'index.html' in url:
        cnum=1
    else:
        cnum = re.findall('index_(\d+).html', url)[0]

    if int(cnum) != int(num):

        if num ==1:
            url=re.sub('index_\d+.html','index.html',url)
        else:
            url=re.sub('index_{0,1}\d*.html','index_%s.html'%num,url)

        # print(url)
        val = driver.find_element_by_xpath('//div[@class="s-list"]//tr[2]//a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="s-list"]//tr[2]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='s-list')
    lis = div.find('table').find_all('tr')[1:]

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a').get_text()
        ggstart_time=tr.find('td',width='80').get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.pingdu.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="s-list"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//td[@class="pagerTitle"][1]').text
        total = re.findall('/(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="news_c"][string-length()>100]')
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

    div = soup.find('div', class_='news_body')

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_yucai_gg", "http://www.pingdu.gov.cn/n3318/n3578/n3590/n3591/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhaobiao_gg", "http://www.pingdu.gov.cn/n3318/n3578/n3590/n3592/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.pingdu.gov.cn/n3318/n3578/n3590/n3593/index.html",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省平度市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "shandong_weihai"], total=2, headless=True, num=1)



