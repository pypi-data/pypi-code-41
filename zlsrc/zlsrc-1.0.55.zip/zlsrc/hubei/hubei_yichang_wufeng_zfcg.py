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
    locator = (By.XPATH, '//tr[@class="xxgklist"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//li[@class="ui-pager focus"]').text

    if int(cnum) != int(num):

        val = driver.find_element_by_xpath('//tr[@class="xxgklist"][1]//a').get_attribute('href')[-20:]
        input_bt=driver.find_element_by_xpath('//input[@class="ui-paging-count"]')
        driver.execute_script('arguments[0].value=%s'%num,input_bt)
        submit_bt=driver.find_element_by_xpath('//li[@class="ui-paging-toolbar"]/a')
        driver.execute_script('arguments[0].click()',submit_bt)
        # 第二个等待
        locator = (By.XPATH, '//tr[@class="xxgklist"][1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('tr',class_='xxgklist')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',class_="bt_date").get_text(strip=True)
        if 'http' in href:
            href = href
        else:
            href = 'http://www.hbwf.gov.cn' + href


        tmp = [name, ggstart_time, href]
        
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@class="xxgklist"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//li[@class="ui-pager"][last()]').text
        total = int(page)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="showBox"][string-length()>200]')
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

    div = soup.find('div',class_="showBox")

    if div == None:
        raise ValueError('div is None')

    return div


data = [

    ["zfcg_zhaobiao_gg", "http://www.hbwf.gov.cn/list-368-1.html#page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.hbwf.gov.cn/list-367-1.html#page=1",["name", "ggstart_time", "href", "info"], f1, f2],



]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省宜昌市五峰县", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "wufengxian"], total=2, headless=False, num=1)



