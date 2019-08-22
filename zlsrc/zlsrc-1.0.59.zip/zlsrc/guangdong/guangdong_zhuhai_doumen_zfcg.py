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

_name_ = 'guangdong_zhuhai_doumen_zfcg'


def f1(driver, num):

    driver.get(re.sub('list2[_\d]*', 'list2_'+str(num) if str(num)!='1' else 'list2' ,driver.current_url))
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='con-right fr']/div[contains(@class,'list_div')]")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='con-right fr']/div[contains(@class,'list_div')]")
    data = []
    for content in content_list:
        name =  content.xpath('./div/a/text()')[0].strip()
        ggstart_time =  content.xpath('./table/tbody/tr/td[1]/text()')[0].strip().split()[-1]
        href = 'http://www.doumen.gov.cn'+content.xpath('./div/a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_temp = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='pagination_index_last']"))).text
    total_page = re.findall('共 (\d+) 页',total_temp)[0]

    driver.quit()
    return int(total_page)


def f3(driver, url):

    driver.get(url)
    if 'pdf' in driver.current_url:

        src = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//embed'))).get_attribute('src')
        return src
    locator = (By.XPATH, "//div[@class='color']")
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
    div = soup.find('div', class_='color')
    return div


data = [
    ["zfcg_zhao_bian_zhong_gg",
     "http://www.doumen.gov.cn/doumen/tzgga/list2_2.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 斗门区人民政府门户网站
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省珠海市斗门区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "guangdong_zhuhai_doumen_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30)
