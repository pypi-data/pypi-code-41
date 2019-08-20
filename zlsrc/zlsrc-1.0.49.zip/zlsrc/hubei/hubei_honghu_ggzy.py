import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zlsrc.util.etl import est_tbs, est_meta, est_html,  add_info



def f1(driver, num):
    locator = (By.XPATH, '(//span[@class="f10"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//select[@id="goToPageEdit"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//select[@id="goToPageEdit"]/option[@selected]').text

    if int(cnum) != int(num):
        val = driver.find_element_by_xpath('(//span[@class="f10"])[1]/a').get_attribute('href')[-20:]
        driver.execute_script('queryFormSubmit(%s);' % num)
        # 第二个等待
        locator = (By.XPATH, '(//span[@class="f10"])[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//select[@id="goToPageEdit"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    lis = soup.find_all('span',class_='f10')

    for tr in lis:
        href = tr.find('a')['href']
        name = tr.find('a').get_text()
        ggstart_time = tr.parent.find_next_sibling('td').get_text().strip('[').strip(']')

        if 'http' in href:
            href = href
        else:
            href = 'http://www.hhztb.com.cn' + href

        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None

    return df


def f2(driver):
    locator = (By.XPATH, '(//span[@class="f10"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//select[@id="goToPageEdit"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//select[@id="goToPageEdit"]/option[last()]').text

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//span[@class="f10"][string-length()>100]')
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

    div = soup.find('td', class_='h2').parent.parent

    if div == None:
        raise ValueError('div is None')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a001&&lcid=1", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a001&&lcid=3", ["name", "ggstart_time", "href", "info"], f1,f2],
    ["gcjs_kongzhijia_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a001&&lcid=4", ["name", "ggstart_time", "href", "info"], f1,f2],
    ["gcjs_zhongbiaohx_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a001&&lcid=7", ["name", "ggstart_time", "href", "info"], f1,f2],

    ["zfcg_zhaobiao_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a005&&lcid=1", ["name", "ggstart_time", "href", "info"], f1,f2],
    ["zfcg_zhongbiaohx_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a005&&lcid=7", ["name", "ggstart_time", "href", "info"], f1,f2],

    ["gcjs_zhaobiao_jiaotong_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a002&&lcid=1", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"交通工程"}),f2],
    ["gcjs_gqita_da_bian_jiaotong_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a002&&lcid=3", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"交通工程"}),f2],
    ["gcjs_kongzhijia_jiaotong_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a002&&lcid=4", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"交通工程"}),f2],
    ["gcjs_zhongbiaohx_jiaotong_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a002&&lcid=7", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"交通工程"}),f2],

    ["gcjs_zhaobiao_shuili_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a003&&lcid=1", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"水利工程"}),f2],
    ["gcjs_kongzhijia_shuili_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a003&&lcid=4", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"水利工程"}),f2],
    ["gcjs_zhongbiaohx_shuili_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a003&&lcid=7", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"水利工程"}),f2],

    ["gcjs_zhaobiao_xinxihua_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a004&&lcid=1", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"信息化工程"}),f2],
    ["gcjs_kongzhijia_xinxihua_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a004&&lcid=4", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"信息化工程"}),f2],
    ["gcjs_zhongbiaohx_xinxihua_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a004&&lcid=7", ["name", "ggstart_time", "href", "info"],add_info(f1,{"gclx":"信息化工程"}),f2],

    ["yiliao_zhaobiao_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a008&&lcid=1", ["name", "ggstart_time", "href", "info"],f1,f2],
    ["yiliao_kongzhijia_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a008&&lcid=4", ["name", "ggstart_time", "href", "info"],f1,f2],
    ["yiliao_zhongbiaohx_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a008&&lcid=7", ["name", "ggstart_time", "href", "info"],f1,f2],

    ["jqita_zhaobiao_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a009&&lcid=1", ["name", "ggstart_time", "href", "info"],f1,f2],
    ["jqita_kongzhijia_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a009&&lcid=4", ["name", "ggstart_time", "href", "info"],f1,f2],
    ["jqita_zhongbiaohx_gg", "http://www.hhztb.com.cn/serinf.do?ggid=a009&&lcid=7", ["name", "ggstart_time", "href", "info"],f1,f2],

]


##zfcg无数据

def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省洪湖市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_honghu"], total=2, headless=False, num=1)



