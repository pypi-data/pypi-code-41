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
from zlsrc.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="hot"]/div[not(@class)][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('index_(\d+).jhtml', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=index_)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//div[@class="hot"]/div[not(@class)][1]//a').get_attribute('href')[-15:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="hot"]/div[not(@class)][1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='hot')
    lis = div.find_all('div',class_="",recursive=False)


    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a').get_text()
        ggstart_time=tr.find('small').get_text().strip('[').strip(']')
        if 'http' in href:
            href = href
        else:
            href = 'http://www.sxzzgs.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="hot"]/div[not(@class)][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        locator = (By.XPATH, '//div[@class="page-large"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.find_element_by_xpath('//div[@class="page-large"]//a[last()-1]').text
        total = int(page)

    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="newsCon"][string-length()>50]')
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

    div = soup.find('div', class_='col-md-12')


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["jqita_zhaobiao_gg", "http://www.sxzzgs.com/zbgg/index_1.jhtml",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_biangeng_gg", "http://www.sxzzgs.com/bggg/index_1.jhtml",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiaohx_gg", "http://www.sxzzgs.com/jggs/index_1.jhtml",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_liubiao_gg", "http://www.sxzzgs.com/cxgg/index_1.jhtml",["name", "ggstart_time", "href", "info"], f1, f2],

]

##山西中招招标代理有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "www_sxzzgs_com"], total=2, headless=True, num=1)



