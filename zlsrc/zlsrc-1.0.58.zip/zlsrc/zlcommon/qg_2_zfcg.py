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

_name_ = 'www_zycg_gov_cn'



def f1(driver, num):
    driver.get(re.sub('page=\d+',  'page=' + str(num) , driver.current_url))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='lby-list']/li[not(@style)]|//table[@class='news']/tbody/tr[position()!=1]")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='lby-list']/li[not(@style)]|//table[@class='news']/tbody/tr[position()!=1]")
    data = []
    for content in content_list:
        name = content.xpath('./a/@title|./td/a/text()')[0].strip()
        href = 'http://www.zycg.gov.cn' + content.xpath('./a/@href|./td/a/@href')[0].strip()
        ggstart_time = content.xpath('./span/text()|./td[3]/text()')[0].strip().strip('[]')
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    total_temp = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//ul[@class='lby-list']/li[last()]/span|//div[@class='pagination']/a[last()-1]"))).text
    if re.match('共(\d+)条',total_temp):
        total_page = re.findall('共(\d+)条',total_temp)[0]
    else:
        total_page = total_temp
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="frame-pane"][string-length()>50]|//body[string-length()>50]')
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

    div = soup.find('div', class_='frame-pane')
    if not div:
        div = soup.find('body')
        div.find('div',class_='head_q').clear()
        div.find('div',class_='tzym').clear()
        div.find('div',class_='nav').clear()
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.zycg.gov.cn/article/llist?catalog=StockAffiche&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.zycg.gov.cn/article/llist?catalog=ZhongBiao&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.zycg.gov.cn/article/llist?catalog=bggg&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.zycg.gov.cn/article/llist?catalog=fbgg&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],



    ["zfcg_yucai_wsjj_gg",
     "http://www.zycg.gov.cn/article/wsjjxq_list?page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://www.zycg.gov.cn/article/wsjjcj_list?page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://www.zycg.gov.cn/article/llist?catalog=wsjjfbgg&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]

# 中央政府采购网
def work(conp, **args):
    '''
    容易封ip，ipNum 加满
    :param conp:
    :param args:
    :return:
    '''
    est_meta(conp, data=data, diqu="中央政府采购网", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_zycg_gov_cn"]
    # driver = webdriver.Chrome()
    # driver.get(data[0][1])
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=50,ipNum=5,num=4)
