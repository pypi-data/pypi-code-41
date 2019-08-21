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
from zlsrc.util.etl import  est_meta, est_html, est_meta_large



def f1(driver, num):
    locator = (By.XPATH, '//table[@class="list"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('curpage=(\d+)&', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=curpage=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//table[@class="list"]//tr[1]//a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//table[@class="list"]//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='list')
    lis = div.find_all('tr')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find_all('td')[-1].get_text().strip('[').strip(']')
        if 'http' in href:
            href = href
        else:
            href = 'http://119.164.253.173:8080' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="list"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    page = driver.find_element_by_xpath('//font[@color="red"]/parent::strong').text
    total = re.findall('/(\d+)', page)[0]
    total = int(total)


    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@id="table3"][string-length()>100]')
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

    div = soup.find('table', id='table3')


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["zfcg_yucai_gg", "http://119.164.253.173:8080/jngp2016/site/list.jsp?curpage=1&colid=121",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg", "http://119.164.253.173:8080/jngp2016/site/list.jsp?curpage=1&colid=37",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://119.164.253.173:8080/jngp2016/site/list.jsp?curpage=1&colid=38",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://119.164.253.173:8080/jngp2016/site/list.jsp?curpage=1&colid=81",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yanshou_gg", "http://119.164.253.173:8080/jngp2016/site/list.jsp?curpage=1&colid=122",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="山东省济南市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "jinan"], total=2, headless=True, num=1)



