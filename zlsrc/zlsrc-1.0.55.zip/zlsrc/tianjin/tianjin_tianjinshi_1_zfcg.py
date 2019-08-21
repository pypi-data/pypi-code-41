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

_name_ = 'tianjin_tianjinshi_zfcg'


def f1(driver, num):
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='dataList']/li[1]/a"))).get_attribute('href')[-20:]
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='selectPage']/a[not(@onclick)]"))).text

    if int(num)!=int(cnum):
        driver.execute_script('findGoodsAndRef(%s,1);'%num)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='dataList']/li[1]/a[not(contains(@href,'%s'))]"%val)))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='dataList']/li")
    data = []
    for content in content_list:
        name = content.xpath('./a/@title')[0].strip()
        href = 'http://tjgp.cz.tj.gov.cn' + content.xpath('./a/@href')[0].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip().strip('[]')
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='countPage']/b"))).text

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
    ["zfcg_zhaobiao_sj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=1665&ver=2&st=1&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],

    ["zfcg_zhaobiao_qj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=1664&ver=2&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'区级'}), f2],
    ["zfcg_biangeng_sj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=1663&ver=2&st=1&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],

    ["zfcg_biangeng_qj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=1666&ver=2&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'区级'}), f2],

    ["zfcg_gqita_zhong_liu_sj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=2014&ver=2&st=1&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],

    ["zfcg_gqita_zhong_liu_qj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=2013&ver=2&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'区级'}), f2],

    ["zfcg_gqita_he_yan_sj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=2015&ver=2&st=1&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],

    ["zfcg_gqita_he_yan_qj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=2016&ver=2&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'区级'}), f2],

    ["zfcg_dyly_sj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=2033&ver=2&st=1&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],

    ["zfcg_dyly_qj_gg",
     "http://tjgp.cz.tj.gov.cn/portal/topicView.do?method=view&view=Infor&id=2034&ver=2&stmp="+str(int(time.time()*1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'区级'}), f2],
]

# 天津市财政局政府采购
def work(conp, **args):
    est_meta(conp, data=data, diqu="天津市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "tianjin_tianjinshi_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30)
