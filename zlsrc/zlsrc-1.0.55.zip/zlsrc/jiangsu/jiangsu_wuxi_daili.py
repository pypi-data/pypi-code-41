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

_name_ = 'jiangsu_wuxi_daili'


def f1(driver, num):
    driver.get(re.sub('Paging=\d+', 'Paging='+str(num),driver.current_url))
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//td[@class='border2' and @height='624']/table/tbody/tr[@height]")))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//td[@class='border2' and @height='624']/table/tbody/tr[@height]")
    data = []
    for content in content_list:
        name =  content.xpath('./td/a/@title')[0].strip()
        ggstart_time =  content.xpath('./td[3]/text()')[0].strip()
        href = 'http://www.wxggzy.com.cn' + content.xpath('./td/a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
#//td[@class='huifont']
    total_temp = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//td[@class='huifont']"))).text
    total_page = re.findall('\/(\d+)',total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']")
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
    div = soup.find('table', id='tblInfo')
    return div


data = [
    ["jqita_gqita_qita_gg",
     "http://www.wxggzy.com.cn/wxcqwz/ggzy/003001/003001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gl_gg",
     "http://www.wxggzy.com.cn/wxcqwz/ggzy/003001/003001005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'国联采购项目'}), f2],
    ["jqita_dyly_gg",
     "http://www.wxggzy.com.cn/wxcqwz/ggzy/003001/003001008/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ###
    ["jqita_zhongbiao_xj_gg",
     "http://www.wxggzy.com.cn/wxcqwz/ggzy/003003/003003005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'询价'}), f2],
    ["jqita_zhongbiao_gl_gg",
     "http://www.wxggzy.com.cn/wxcqwz/ggzy/003003/003003006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'国联采购项目'}), f2],
    ["jqita_dyly_gg",
     "http://www.wxggzy.com.cn/wxcqwz/ggzy/003003/003003008/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_qita_gg",
     "http://www.wxggzy.com.cn/wxcqwz/ggzy/003003/003003004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]

#无锡市股权登记托管中心有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省无锡市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "jiangsu_wuxi_daili"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30, ipNum=0)
