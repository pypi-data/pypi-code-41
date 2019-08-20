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
    locator = (By.XPATH, '(//div[@class="newListwenzi"]//tr[1]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//a[@class="pagreActive"]').text


    if int(cnum) != int(num):

        val = driver.find_element_by_xpath('(//div[@class="newListwenzi"]//tr[1]//a)[1]').get_attribute('href')[-30:]
        driver.execute_script('pagination(%s);'%num)
        # 第二个等待
        locator = (By.XPATH, '(//div[@class="newListwenzi"]//tr[1]//a)[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='newListwenzi')
    lis = div.find_all('tr')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('td',width='35%').get_text()
        ggstart_time=re.findall('\d+-\d+-\d+',ggstart_time)[0]
        laiyuan=tr.find_all('a')
        if len(laiyuan)==2:
            laiyuan=laiyuan[1].get_text().strip()
            info=json.dumps({'laiyuan':laiyuan},ensure_ascii=False)
        else:
            info=None
        if 'http' in href:
            href = href
        else:
            href = 'https://www.hbggzyfwpt.cn' + href

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)


    return df


def f2(driver):
    locator = (By.XPATH, '(//div[@class="newListwenzi"]//tr[1]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="mmggxlh"]/a[last()-1]').text

    driver.quit()
    return int(total)

def chang_time(f):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '(//div[@class="newListwenzi"]//tr[1]//a)[1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        ctext=driver.find_element_by_xpath('//p[@id="publishTime"]/a[@class="searchAActive"]').text
        if ctext == '当天':

            total = driver.find_element_by_xpath('//div[@class="mmggxlh"]/a[last()-1]').text
            driver.execute_script('publishTime(3)')
            locator = (By.XPATH, '//div[@class="mmggxlh"]/a[last()-1][(string() != %s)]'%total)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner





def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="detailNeirong"][string-length()>100]')
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

    div = soup.find('div', id='detail').parent

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_gqita_zhuce_gg", "https://www.hbggzyfwpt.cn/jyxx/jsgcXmxx",["name", "ggstart_time", "href", "info"], chang_time(add_info(f1,{"gclx":"项目注册"})), chang_time(f2)],
    ["gcjs_zhaobiao_gg", "https://www.hbggzyfwpt.cn/jyxx/jsgcZbgg",["name", "ggstart_time", "href", "info"], chang_time(f1), chang_time(f2)],
    ["gcjs_kaibiao_gg", "https://www.hbggzyfwpt.cn/jyxx/jsgcKbjl",["name", "ggstart_time", "href", "info"], chang_time(f1), chang_time(f2)],
    ["gcjs_zhongbiaohx_gg", "https://www.hbggzyfwpt.cn/jyxx/jsgcpbjggs",["name", "ggstart_time", "href", "info"], chang_time(f1), chang_time(f2)],
    ["gcjs_zhongbiao_gg", "https://www.hbggzyfwpt.cn/jyxx/jsgcZbjggs",["name", "ggstart_time", "href", "info"], chang_time(f1), chang_time(f2)],

    ["zfcg_zhaobiao_gg", "https://www.hbggzyfwpt.cn/jyxx/zfcg/cggg",["name", "ggstart_time", "href", "info"], chang_time(f1), chang_time(f2)],
    ["zfcg_biangeng_gg", "https://www.hbggzyfwpt.cn/jyxx/zfcg/gzsxs",["name", "ggstart_time", "href", "info"], chang_time(f1), chang_time(f2)],
    ["zfcg_zhongbiao_gg", "https://www.hbggzyfwpt.cn/jyxx/zfcg/zbjggs",["name", "ggstart_time", "href", "info"], chang_time(f1), chang_time(f2)],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_hubei"], total=2, headless=False, num=1)



