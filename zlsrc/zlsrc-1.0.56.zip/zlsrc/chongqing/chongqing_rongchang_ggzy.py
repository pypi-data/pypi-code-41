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
    locator = (By.XPATH, '//li[@class="news-li"][1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum=re.findall('_(\d+)',url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=_)\d+',str(num),url)

        val = driver.find_element_by_xpath('//li[@class="news-li"][1]/a').get_attribute('href')[-15:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//li[@class="news-li"][1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find_all('li',class_='news-li')

    for tr in div:

        href=tr.a['href']
        name=tr.a.find('span',class_='news-title').get_text(strip=True)
        ggstart_time=tr.a.find('span',class_='news-date').get_text(strip=True)
        tmp = [name, ggstart_time, href]

        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="news-li"][1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    page = driver.find_element_by_link_text('末页').get_attribute('href')
    total=re.findall('_(\d+)',page)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="left w2"][string-length()>100]')
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

    div = soup.find('div',class_="left w2")


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://zyjy.rongchang.gov.cn/node/1700_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://zyjy.rongchang.gov.cn/node/1701_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://zyjy.rongchang.gov.cn/node/1702_1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://zyjy.rongchang.gov.cn/node/1703_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://zyjy.rongchang.gov.cn/node/1705_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_da_bian_gg", "http://zyjy.rongchang.gov.cn/node/1706_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_dyly_gg", "http://zyjy.rongchang.gov.cn/node/1708_1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg", "http://zyjy.rongchang.gov.cn/node/1715_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_zhongbiao_gg", "http://zyjy.rongchang.gov.cn/node/1716_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_gqita_da_bian_gg", "http://zyjy.rongchang.gov.cn/node/1717_1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg", "http://zyjy.rongchang.gov.cn/node/1718_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiao_gg", "http://zyjy.rongchang.gov.cn/node/1720_1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_da_bian_gg", "http://zyjy.rongchang.gov.cn/node/1721_1",["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市荣昌区", **args)
    est_html(conp, f=f3, **args)




if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "rongchang"], total=2, headless=True, num=1)



