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
    locator = (By.XPATH, '//div[@class="queryTbBox"]/table/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//span[@class="current"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//span[@class="current"]').text

    if int(cnum) != int(num):

        val = driver.find_element_by_xpath('//div[@class="queryTbBox"]/table/tbody/tr[1]//a').get_attribute('href')[-30:]
        driver.execute_script('javascript:jumpPage(%s);'%num)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="queryTbBox"]/table/tbody/tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//span[@class="current"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='queryTbBox').table.tbody
    lis = div.find_all('tr')

    for tr in lis:
        tds=tr.find_all('td')
        href = tr.find('a')['href']
        name = tr.find('a')['title']
        xm_type=tds[1].get_text()
        dw=tds[2].span['title']
        ggstart_time=tds[3].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.soeasyjc.com' + href

        info=json.dumps({'xm_type':xm_type,"dw":dw},ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="queryTbBox"]/table/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    try:
        locator = (By.XPATH, '//span[@class="current"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.find_element_by_xpath('//div[@class="manu"]/a[last()]').get_attribute('href')
        total = re.findall('\d+',page)[0]

    except:
        total = 1

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="mymain"][string-length()>100]')
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

    div = soup.find('div', class_='maincontent')

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["qycg_zhaobiao_gg", "http://www.soeasyjc.com/newTender?infoType=1&submitByForm=Y", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_gg", "http://www.soeasyjc.com/newTender?infoType=2&submitByForm=Y", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_2_gg", "http://www.soeasyjc.com/newTender?infoType=3&submitByForm=Y", ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="高校竞价网", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "www_soeasyjc_com"], total=2, headless=True, num=1)



