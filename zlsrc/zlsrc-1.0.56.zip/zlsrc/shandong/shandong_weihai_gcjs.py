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
    locator = (By.XPATH, '//div[@class="info_con"]/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageIndex=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=pageIndex=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//div[@class="info_con"]/table//tr[1]//a').get_attribute('href')[-30:]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//div[@class="info_con"]/table//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='info_con')
    lis = div.find('table').find_all('tr')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',width='15%').get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://60.212.191.165:10000' + href
        tag=tr.find('a').get_text().strip()
        tag=re.findall('\[.+\]',tag)[0]
        info=json.dumps({'tag':tag},ensure_ascii=False)

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="info_con"]/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//div[@class="pages"]/a[last()]').get_attribute('href')
        total = re.findall('pageIndex=(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//table[@width='800px' and @align='center'][string-length()>50] | //table[@width='80%' and @align='center'][string-length()>50]")
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

    div = soup.find('table', attrs={'width':'800px','align':'center'})
    if div == None:
        div = soup.find('table', attrs={'width': '80%', 'align': 'center'}).parent


    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zgys_gg", "http://60.212.191.165:10000/Tradeinfo-GGGSList/1-0-1?pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhaobiao_gg", "http://60.212.191.165:10000/Tradeinfo-GGGSList/1-0-0?pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongzhi_gg", "http://60.212.191.165:10000/Tradeinfo-GGGSList/1-0-7?pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg", "http://60.212.191.165:10000/Tradeinfo-GGGSList/1-0-3?pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://60.212.191.165:10000/Tradeinfo-GGGSList/1-0-8?pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省威海市", **args)
    est_html(conp, f=f3, **args)

# 修改时间：2019/8/14
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "shandong_weihai"], total=2, headless=True, num=1)


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     # print(url)
    #     # driver.get(url)
    #     # df = f2(driver)
    #     # print(df)
    #     # driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 2)
    #     # print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://60.212.191.165:10000/TradeDetals-ZtbShow/297-5071-0-3-0/6ba75ba2-65ba-471b-8a76-bddb75ac92e9')
    # print(df)
