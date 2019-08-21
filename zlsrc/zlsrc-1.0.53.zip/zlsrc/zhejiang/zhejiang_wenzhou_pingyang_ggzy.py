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

_name_ = 'zhejiang_wenzhou_pingyang_ggzy'


def f1(driver, num):
    driver.get(re.sub('Paging=\d+', 'Paging='+str(num) ,driver.current_url))
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='data']/table/tbody/tr[@height]")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='data']/table/tbody/tr[@height]")
    data = []
    for content in content_list:
        name =  content.xpath('./td/a/text()')[0].strip()
        ggstart_time =  content.xpath('./td[3]/text()')[0].strip()
        href = 'http://www.pyztb.com'+content.xpath('./td/a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
        #//td[@id='Paging']/table/tbody/tr/td/font[2]/b
    locator = (By.XPATH, "//td[@class='huifont']")
    total_temp=WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    total_page = re.findall('/(\d+)',total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='row']")
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
    div = soup.find('div', class_='row')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.pyztb.com/TPFront/jyxx/004001/004001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_dayi_gg",
     "http://www.pyztb.com/TPFront/jyxx/004001/004001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.pyztb.com/TPFront/jyxx/004001/004001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.pyztb.com/TPFront/jyxx/004001/004001005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ############
    ["zfcg_zhaobiao_gg",
     "http://www.pyztb.com/TPFront/jyxx/004002/004002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.pyztb.com/TPFront/jyxx/004002/004002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_dyly_gg",
     "http://www.pyztb.com/TPFront/jyxx/004002/004002004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_hetong_gg",
     "http://www.pyztb.com/TPFront/jyxx/004002/004002005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_zhong_liu_gg",
     "http://www.pyztb.com/TPFront/jyxx/004002/004002006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ############
    ["qsy_zhaobiao_gg",
     "http://www.pyztb.com/TPFront/jyxx/004003/004003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_biangeng_gg",
     "http://www.pyztb.com/TPFront/jyxx/004003/004003003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_dyly_gg",
     "http://www.pyztb.com/TPFront/jyxx/004003/004003004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_hetong_gg",
     "http://www.pyztb.com/TPFront/jyxx/004003/004003005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qsy_gqita_zhong_liu_gg",
     "http://www.pyztb.com/TPFront/jyxx/004003/004003006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ############
    ["gcjs_zhaobiao_xz_gg",
     "http://www.pyztb.com/TPFront/jyxx/004006/004006001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":'乡镇'}), f2],
    ["gcjs_zhongbiao_xz_gg",
     "http://www.pyztb.com/TPFront/jyxx/004006/004006002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":'乡镇'}), f2],

]

# 浙江温州平阳县公共资源交易中
def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省温州市平阳县", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "zhejiang_wenzhou_pingyang_ggzy",]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    # work(conp,headless=False,long_ip=False)
