import json
import random
import re
from datetime import datetime

import math
import requests
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'qycg_txzb_miit_gov_cn'


def f1(driver, num):
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//table[@id='newsItem']/tbody/tr[1]/td/a"))).get_attribute('href')[-30:]
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@id='page']"))).get_attribute('value')

    if int(num)!=int(cnum):
        driver.execute_script('page(%s)'%num)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//table[@id='newsItem']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]"%val)))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[@id='newsItem']/tbody/tr")
    data = []
    for content in content_list:
        tmp =  content.xpath('./td/a/text()')[0].strip().split('')
        name, ggstart_time = tmp[0],tmp[-1]
        href = 'https://txzb.miit.gov.cn' + re.findall("\'([^\']+)\'",content.xpath('./td/a/@href')[0].strip())[0]
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//td[@class="page STYLE1 STYLE4" and string()="尾页"]'))).get_attribute('page')

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@style='width: 260mm;']")
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
    div = soup.find('table', style='width: 260mm;')
    return div


data = [
    ["zfcg_gqita_zhao_zgys_liu_gg",
     "https://txzb.miit.gov.cn/DispatchAction.do?efFormEname=POIX14&pagesize=11",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "https://txzb.miit.gov.cn/DispatchAction.do?efFormEname=POIX62&methodName=queryZhongbiao&pagesize=11",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

#中华人民共和国工业和信息化部
def work(conp, **args):
    est_meta(conp, data=data, diqu="中华人民共和国工业和信息化部", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qycg_txzb_miit_gov_cn"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30,headless=False)
