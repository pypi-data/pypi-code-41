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

_name_ = 'jiangsu_changzhoushi_wujinqu_ggzy'


def f1(driver, num):

    driver.get(re.sub('Paging=\d+', 'Paging='+str(num) ,driver.current_url))
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//table[@cellspacing='0' and @align='center' and @valign='top']")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[@cellspacing='0' and @align='center' and @valign='top']/tbody/tr[@height='22']")
    data = []
    for content in content_list:
        name =  content.xpath('./td/a/@title')[0].strip()
        ggstart_time =  content.xpath('./td[3]/text()')[0].strip()
        href = 'http://218.93.116.250:8000' + content.xpath('./td/a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
        #//td[@id='Paging']/table/tbody/tr/td/font[2]/b
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//td[@id='Paging']/table/tbody/tr/td/font[2]/b"))).text

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@width='964']/table[@width='100%']")
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
    div = soup.find('td', width='964')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004001/004001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004001/004001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004002/004002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004002/004002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004002/004002003//?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_dyly_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004002/004002004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],




    ["yiliao_zhaobiao_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004003/004003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_biangeng_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004003/004003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhongbiao_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004003/004003003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_dyly_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004003/004003004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


###########
    ["gcjs_zhaobiao_xz_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004006/004006001/004006001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇'}), f2],

    ["gcjs_biangeng_xz_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004006/004006001/004006001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇'}), f2],

    ["gcjs_zhongbiaohx_xz_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004006/004006001/004006001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇'}), f2],

    ["zfcg_zhaobiao_xz_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004006/004006002/004006002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇'}), f2],

    ["zfcg_biangeng_xz_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004006/004006002/004006002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇'}), f2],

    ["zfcg_zhongbiaohx_xz_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004006/004006002/004006002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇'}), f2],

    ["zfcg_dyly_xz_gg",
     "http://218.93.116.250:8000/wjweb/ggxx/004006/004006002/004006002004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'乡镇'}), f2],

]

# 江苏常州武进区公共资源
def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省常州市武进区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "jiangsu_changzhoushi_wujinqu_ggzy"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30)
