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
    locator = (By.XPATH, '(//div[@class="is-tda"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=page=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('(//div[@class="is-tda"])[1]/a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '(//div[@class="is-tda"])[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table',class_='is-xxgkTable archive_area').find_all('tr',attrs={'class':True})[1:]

    for tr in div:
        href=tr.find('a')['href']
        name=tr.find('a').get_text(strip=True)
        ggstart_time=tr.find_all('td')[-1].get_text(strip=True)
        pro_index=tr.find_all('td')[-2].get_text(strip=True)
        if 'http' in href:
            href = href
        else:
            href = 'http://www.luan.gov.cn' + href

        info=json.dumps({'pro_index':pro_index},ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '(//div[@class="is-tda"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    page = driver.find_element_by_xpath('//div[@id="page_list"]/a[last()-1]').get_attribute('href')
    total=re.findall('page=(\d+)',page)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="zoom"][string-length()>50]')
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

    div = soup.find('div',class_="is-contentbox")


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["zfcg_zhaobiao_gg", "http://www.luan.gov.cn/opennessTarget/?branch_id=5212bc2d682e09147c7c4a8a&column_code=171102&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_zhong_liu_gg", "http://www.luan.gov.cn/opennessTarget/?branch_id=5212bc2d682e09147c7c4a8a&column_code=171103&page=1",["name", "ggstart_time", "href", "info"], f1, f2],

]

###六安市人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省六安市", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "luan"], total=2, headless=True, num=1)


