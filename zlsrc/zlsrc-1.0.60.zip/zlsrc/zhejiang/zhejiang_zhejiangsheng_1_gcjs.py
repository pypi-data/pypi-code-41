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

    locator = (By.XPATH, '//div[@id="content_list"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//div[@class="page"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=driver.find_element_by_link_text('下一页').get_attribute('onclick')

    if 'false' in cnum:
        cnum=driver.find_element_by_link_text('上一页').get_attribute('onclick')
        cnum = int(re.findall('javascript:showNews\((\d+)\)', cnum)[0]) + 1
    else:
        cnum=int(re.findall('javascript:showNews\((\d+)\)',cnum)[0])-1


    if int(cnum) != int(num):
        val = driver.find_element_by_xpath('//div[@id="content_list"]//tr[1]//a').get_attribute('href')[
              -30:]
        driver.execute_script('showNews(%s);' % num)

        # 第二个等待
        locator = (By.XPATH, '//div[@id="content_list"]//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//div[@class="page"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', id='content_list')
    lis = div.find_all('tr')

    for tr in lis:
        href = tr.find('a')['href']
        name = tr.find('a')['title']
        ggstart_time = tr.find('td',width='13%').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.zjt.gov.cn' + href

        tmp = [name, ggstart_time, href]
        
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="content_list"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@class="page"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//div[@class="page"]/a[last()]').get_attribute('onclick')

    total = re.findall('javascript:showNews\((\d+)\)', total)[0]

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
    ["gcjs_zhaobiao_gg", "http://www.zjt.gov.cn/col/col26/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.zjt.gov.cn/col/col27/index.html",["name", "ggstart_time", "href", "info"], f1, f2],

]


##浙江交通运输厅

def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "jiaotong"], total=4, headless=False, num=1)



