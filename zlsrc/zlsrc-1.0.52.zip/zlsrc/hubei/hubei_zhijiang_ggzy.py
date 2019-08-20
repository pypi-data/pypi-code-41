from collections import OrderedDict
from pprint import pprint

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
from zlsrc.util.etl import  est_meta, est_html,  add_info



def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageing=(\d+)', url)[0]

    if int(cnum) != int(num):
        url=re.sub('(?<=pageing=)\d+',str(num),url)
        # print(url)
        val = driver.find_element_by_xpath('//ul[@class="list"]/li[1]/a').get_attribute('href')[-40:-20]
        driver.get(url)

        # 第二个等待
        locator = (By.XPATH, '//ul[@class="list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('li', class_='list-item')

    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span',class_="list-date").get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.zgzhijiang.gov.cn' + href

        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//a[@class="wb-page-default wb-page-number wb-page-family"]').text
        total = re.findall('/(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="mainContent"][string-length()>100]')
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

    div = soup.find('div', class_="detail-main")

    if div == None:
        raise ValueError('div is None')

    return div


def get_data():
    data = []

    # gcjs
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("gqita_da_bian", "002"),
                           ("zhongbiaohx", "003"), ("zhongbiao", "004"), ("liubiao", "005")])
    # zfcg
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003"), ("liubiao", "004"), ("yucai", "005")])

    ##gcjs
    adtype1 = OrderedDict([('施工', 'shigong,001'), ("监理", "jianli,002"),
                           ("勘察设计", "kancha,003"), ("其他", "qita,004")])
    ##zfcg
    adtype2 = OrderedDict([('货物', 'huowu,001'), ("服务", "fuwu,002"),("工程", "gongcheng,003")])

    # gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003001/003001{jy}/003001{jy}{dq}/?pageing=1".format(dq=adtype1[w2].split(',')[1],
                                                                                  jy=ggtype1[w1])
            tmp = ["gcjs_%s_%s_gg" % (w1, adtype1[w2].split(',')[0]), href,
                   ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    ##zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype2.keys():
            href = "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003002/003002{jy}/003002{jy}{dq}/?pageing=1".format(dq=adtype2[w2].split(',')[1],
                                                                                  jy=ggtype2[w1])
            tmp = ["zfcg_%s_%s_gg" % (w1, adtype2[w2].split(',')[0]), href,
                   ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    data1 = data.copy()
    remove=['zfcg_yucai_gongcheng_gg',]
    for i in data1:
        if i[0] in remove:
            data1.remove(i)

    data2 = [

        ["jqita_zhaobiao_gg", "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003008/003008001/?pageing=1",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': "乡镇及其他"}), f2],
        ["jqita_biangeng_gg", "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003008/003008002/?pageing=1",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': "乡镇及其他"}), f2],
        ["jqita_zhongbiao_gg", "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003008/003008003/?pageing=1",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': "乡镇及其他"}), f2],

        ["qsy_zhaobiao_gg", "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003007/003007001/?pageing=1",
         ["name", "ggstart_time", "href", "info"], f1, f2],
        ["qsy_biangeng_gg", "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003007/003007002/?pageing=1",
         ["name", "ggstart_time", "href", "info"], f1, f2],
        ["qsy_zhongbiao_gg", "http://ggzyjy.zgzhijiang.gov.cn/zjSite/jyxx/003007/003007003/?pageing=1",
         ["name", "ggstart_time", "href", "info"], f1, f2],

    ]
    data1.extend(data2)


    return data1


data = get_data()

# pprint(data)



def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省枝江市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_zhijiang"], total=2, headless=False, num=1)
    pass


