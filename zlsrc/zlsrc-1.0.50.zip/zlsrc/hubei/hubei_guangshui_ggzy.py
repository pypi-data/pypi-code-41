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
from zlsrc.util.etl import est_tbs, est_meta, est_html




def f1(driver, num):
    locator = (By.XPATH, '//div[@id="listCon"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//span[@class="page-cur"]').text
    url=driver.current_url
    mark=url.rsplit('=',maxsplit=1)[1]

    if int(cnum) != int(num):

        val = driver.find_element_by_xpath('//div[@id="listCon"]//li[1]/a').get_attribute('href')[-20:]
        driver.execute_script('SearchArticleOnce(%s,0,%s,10)'%(mark,num))
        # 第二个等待
        locator = (By.XPATH, '//div[@id="listCon"]//li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', id='listCon')
    lis = div.find_all('li')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://59.173.16.12' + href

        tmp = [name, ggstart_time, href]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="listCon"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//a[@class="page-end"]').get_attribute('onclick')
    total=re.findall('SearchArticleOnce\(\d+?,0,(\d+),10\)',total)[0]

    driver.quit()
    return int(total)




def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="content"][string-length()>50]')
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

    div = soup.find('div', class_='new_detail')

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://59.173.16.12/Category/More?id=676",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://59.173.16.12/Category/More?id=678",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://59.173.16.12/Category/More?id=680",["name", "ggstart_time", "href", "info"], f1, f2],

]

##zfcg无数据

def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省广水市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_guangshui"], total=2, headless=True, num=1)



