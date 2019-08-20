import json
import random
import re
from datetime import datetime

import math
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time



def f1(driver, num):
    try:
        locator = (By.XPATH, '//td[@class="huifont"]')
        txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    except:
        driver.refresh()
        locator = (By.XPATH, '//td[@class="huifont"]')
        txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)\/', txt)[0]

    locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr/td/a')

    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]

    if int(cnum) != int(num):
        new_url = re.sub('Paging=\d*', 'Paging=' + str(num), driver.current_url)

        driver.get(new_url)
        try:
            locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr/td/a[not(contains(@href,"%s"))]' % (val))
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr/td/a[not(contains(@href,"%s"))]' % (val))
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="moreinfocon"]/tbody/tr')

    data = []
    for con in content_list:
        name = con.xpath("./td/a/@title")[0].strip()

        url = 'http://ztb.shangyu.gov.cn' + con.xpath("./td/a/@href")[0].strip()

        ggstart_time = con.xpath("./td[3]/span/text()")[0].strip()

        temp = [name, ggstart_time, url]

        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//td[@class="huifont"]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    total_page = re.findall('\/(\d+)',txt)[0]

    driver.quit()

    return int(total_page)


def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH, '//table[@width="887"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('table', width='887')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgg/006001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_dayi_gg",
     "http://ztb.shangyu.gov.cn/syqztb/dybc/018001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgs/007001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ztb.shangyu.gov.cn/syqztb/cjxx/008001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_yucai_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgg/006003/006003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgg/006003/006003006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_zhong_liu_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgs/007002/007002006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["qsy_zhaobiao_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgg/006010/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhongbiao_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgs/007005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_zhaobiao_xz_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgg/006005/006005001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇街道、部门两区'}), f2],
    ["gcjs_zhongbiaohx_xz_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgs/007004/007004001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇街道、部门两区'}), f2],
    ["gcjs_zhongbiao_xz_gg",
     "http://ztb.shangyu.gov.cn/syqztb/cjxx/008005/008005001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇街道、部门两区'}), f2],

    ["zfcg_yucai_xz_gg",
     "http://ztb.shangyu.gov.cn/syqztb/cggs/034001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇街道、部门两区'}), f2],
    ["zfcg_zhaobiao_xz_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgg/006005/006005002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇街道、部门两区'}), f2],

    ["zfcg_zhongbiao_xz_gg",
     "http://ztb.shangyu.gov.cn/syqztb/zbgs/007004/007004002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇街道、部门两区'}), f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省绍兴市上虞区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_shaoxing_shangyuqu"]
    # driver=webdriver.Chrome()
    # driver.get('http://www.ceiea.com/stock/0_11.htm')
    # f2(driver)
    # print(f1(driver, 3).values.tolist())
    work(conp)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     df_list = f1(driver, i).values.tolist()
    #     # print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
