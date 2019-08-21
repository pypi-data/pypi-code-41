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
from zlsrc.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info



def f1(driver, num):
    locator = (By.XPATH, '//table[@class="moreinfocon"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=Paging=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//table[@class="moreinfocon"]//tr[1]//a').get_attribute('href')[-40:-20]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//table[@class="moreinfocon"]//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='moreinfocon')
    lis = div.find_all('tr',height="28")

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',align="right").get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.zxsztb.org' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="moreinfocon"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//td[@class="huifont"]').text
        total = re.findall('/(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="mainContent"][string-length()>50][count(*)>=1]')
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

    div = soup.find('div',class_="detail-content")

    if div == None:
        raise ValueError('div is None')

    return div


data = [

    ["gcjs_gqita_hezhun_gg", "http://www.zxsztb.org/TPFront/jyxx/002001/002001001/?Paging=1 ",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"项目核准"}), f2],
    ["gcjs_zhaobiao_gg", "http://www.zxsztb.org/TPFront/jyxx/002001/002001002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://www.zxsztb.org/TPFront/jyxx/002001/002001003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.zxsztb.org/TPFront/jyxx/002001/002001004/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.zxsztb.org/TPFront/jyxx/002001/002001005/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.zxsztb.org/TPFront/jyxx/002002/002002001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://www.zxsztb.org/TPFront/jyxx/002002/002002002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.zxsztb.org/TPFront/jyxx/002002/002002003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg", "http://www.zxsztb.org/TPFront/jyxx/002004/002004001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_biangeng_gg", "http://www.zxsztb.org/TPFront/jyxx/002004/002004002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_zhongbiao_gg", "http://www.zxsztb.org/TPFront/jyxx/002004/002004003/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省钟祥市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_zhongxiang"], total=2, headless=False, num=1)



