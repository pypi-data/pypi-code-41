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




def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url

    if 'aboutjyxxsearch.html' in url:
        cnum=1
    else:
        cnum=re.findall('/(\d+).html',url)[0]

    if int(cnum) != num:
        url = url.rsplit('/', maxsplit=1)[0] + '/%s.html'%num
        val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute('href')[-30:-5]

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='wb-data-item')
    trs = div.find_all('li')

    for tr in trs:

        href = tr.div.a['href']
        name2 = tr.div.a['title']
        name1=re.findall("</font>(.+?)<font",name2)
        name = name1[0] if name1 else name2

        ggstart_time = tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.xxz.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    while True:
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        try:
            url=driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-hover"]/preceding-sibling::li[1]/a').get_attribute('href')
        except:
            total=1
            break
        total = re.findall('/(\d+?).html', url)[0]
        driver.get(url)

        time.sleep(0.5)
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//div[@id="static"]//div[@class="ewb-page"]')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        try:
            url = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-hover"]/a').get_attribute('href')

            driver.get(url)
            time.sleep(0.5)
        except:
            break

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-article-info"][string-length()>50]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
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
    div = soup.find('div',class_='imp')

    return div



data=[
    ["gcjs_zhaobiao_gg","http://ggzyjy.xxz.gov.cn/jyxx/005001/005001001/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_biangeng_gg","http://ggzyjy.xxz.gov.cn/jyxx/005001/005001002/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_dayi_gg","http://ggzyjy.xxz.gov.cn/jyxx/005001/005001003/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://ggzyjy.xxz.gov.cn/jyxx/005001/005001004/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://ggzyjy.xxz.gov.cn/jyxx/005002/005002001/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_biangeng_gg","http://ggzyjy.xxz.gov.cn/jyxx/005002/005002002/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_dayi_gg","http://ggzyjy.xxz.gov.cn/jyxx/005002/005002003/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://ggzyjy.xxz.gov.cn/jyxx/005002/005002004/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],

    ["yiliao_zhaobiao_gg","http://ggzyjy.xxz.gov.cn/jyxx/005003/005003001/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["yiliao_biangeng_gg","http://ggzyjy.xxz.gov.cn/jyxx/005003/005003002/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],
    ["yiliao_zhongbiao_gg","http://ggzyjy.xxz.gov.cn/jyxx/005003/005003004/aboutjyxxsearch.html",["name","ggstart_time","href","info"],f1,f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省湘西市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hunan_xiangxi"], pageLoadStrategy='none',total=2, headless=False, num=1)



