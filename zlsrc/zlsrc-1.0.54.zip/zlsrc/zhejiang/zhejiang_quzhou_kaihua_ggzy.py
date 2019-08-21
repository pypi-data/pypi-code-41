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
    locator = (By.XPATH, '//div[@class="default_pgContainer"]//table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageNum=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=pageNum=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//div[@class="default_pgContainer"]//table//tr[1]//a').get_attribute('href')[-30:]
        driver.get(url)
        # 第二个等待
        locator = (By.XPATH, '//div[@class="default_pgContainer"]//table//tr[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='default_pgContainer').find('table')
    lis = div.find_all('tr')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a').get_text(strip=True)
        ggstart_time=tr.find_all('td')[-1].get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.kaihua.gov.cn' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]//table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//span[@class="default_pgTotalPage"]').text
    total = int(page)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//td[@class="bt_content"][string-length()>40] | //div[@class="detail-content"][string-length()>30]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        falg = 1
    except:
        locator = (By.XPATH, "//div[@class='Main-p'][string-length()>30]  |  //div[@class='Main-p']//img")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
        falg = 2
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
    if falg == 1:
        div = soup.find('table',id="c")
        if div == None:
            div = soup.find('div', class_='detail-content').parent
    elif falg == 2:
        div = soup.find('div', class_='Main-p').parent
    else:raise ValueError
    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.kaihua.gov.cn/col/col1384138/index.html?uid=4855243&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.kaihua.gov.cn/col/col1384139/index.html?uid=4442405&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.kaihua.gov.cn/col/col1384140/index.html?uid=4442405&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_dyly_gg", "http://www.kaihua.gov.cn/col/col1384142/index.html?uid=4839715&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg", "http://www.kaihua.gov.cn/col/col1384143/index.html?uid=4839715&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.kaihua.gov.cn/col/col1384144/index.html?uid=4839715&pageNum=1",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省衢州市开化县", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "xinajuxian"], total=2, headless=True, num=1)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://www.kaihua.gov.cn/art/2018/1/4/art_1384138_14815358.html')
    # print(df)




