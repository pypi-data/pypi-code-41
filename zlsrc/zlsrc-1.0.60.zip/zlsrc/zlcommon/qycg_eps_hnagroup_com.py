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

_name_ = 'qycg_eps_hnagroup_com'



def f1(driver, num):
    # print(driver.current_url[-10:],'-----',re.sub('offset=\d+',  'offset=' + str((int(num)-1) * 10), driver.current_url)[-10:])
    driver.get(re.sub('offset=\d+',  'offset=' + str((int(num)-1) * 10), driver.current_url))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//form[@id='listFormId']/table/tbody/tr[not(@style)][count(child::td)>2]")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//form[@id='listFormId']/table/tbody/tr[not(@style)][count(child::td)>2]")
    data = []
    for content in content_list:
        name = content.xpath('./td/a/@title|./td/a/text()')[0].strip()
        comp = content.xpath('./td[3]/text()')[0].strip()
        href = 'http://eps.hnagroup.com/jc/' + content.xpath('./td/a/@href')[0].strip()
        ggstart_time = content.xpath('./td[last()]/text()')[0].strip()
        info = json.dumps({"comp":comp},ensure_ascii=False)
        temp = [name, ggstart_time, href,info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    total_tem = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='pageDiv']"))).text
    total_page = re.findall('共:(\d+)页',total_tem)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="row"]')
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
    ["qycg_zhongbiao_gg",
     "http://eps.hnagroup.com/jc/auctionHeader/selectList.html?pager.offset=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_dyly_gg",
     "http://eps.hnagroup.com/jc/infocenter/selectList.html?pager.offset=0",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]

#海航集团有限公司
def work(conp, **args):

    est_meta(conp, data=data, diqu="海航集团有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "qycg_eps_hnagroup_com"]
    driver = webdriver.Chrome()
    driver.get(data[0][1])
    # print(f2(driver))

    f1(driver, 9)
    f1(driver, 10)
    # work(conp,total=100,thread_retry=3,retry=3,pageloadtimeout=60,ipNum=1)
