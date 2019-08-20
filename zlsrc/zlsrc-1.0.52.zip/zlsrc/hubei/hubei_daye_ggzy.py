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
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('/(\d+?).html', url)[0]

    if int(cnum) != int(num):
        url=re.sub('\d+(?=.html)',str(num),url)

        val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]//a').get_attribute('href')[-30:-5]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('ul', class_='wb-data-item').find_all('li')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span',class_="wb-data-date").get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://111.4.115.225:8010' + href

        tmp = [name, ggstart_time, href]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):

    while True:
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            url=driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-hover"]/preceding-sibling::li[1]/a').get_attribute('href')
        except:
            total = driver.find_element_by_xpath(
                '//li[@class="ewb-page-li ewb-page-hover"]/preceding-sibling::li[1]').text
            driver.quit()
            return int(total)
        driver.get(url)
        total= re.findall('/(\d+?).html', url)[0]
        time.sleep(1)
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            url = driver.find_element_by_xpath(
            '//li[@class="ewb-page-li ewb-page-hover"]/a').get_attribute('href')

            driver.get(url)
            time.sleep(1)
        except:
            break

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-detail-text"][string-length()>100]')
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

    div = soup.find('div', class_="ewb-detail")
    div.find('div',class_='ewb-bar clearfix').extract()

    if div == None:
        raise ValueError('div is None')

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://111.4.115.225:8010/ztb/jyxx/001001/001001001/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://111.4.115.225:8010/ztb/jyxx/001001/001001002/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://111.4.115.225:8010/ztb/jyxx/001001/001001003/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://111.4.115.225:8010/ztb/jyxx/001001/001001004/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://111.4.115.225:8010/ztb/jyxx/001001/001001005/1.html",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://111.4.115.225:8010/ztb/jyxx/001002/001002001/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://111.4.115.225:8010/ztb/jyxx/001002/001002002/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://111.4.115.225:8010/ztb/jyxx/001002/001002003/1.html",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省大冶市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_daye"], total=2, headless=False, num=1)



