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

_name_ = 'anhui_bengbu_zfcg'


def f1(driver, num):

    driver.get(re.sub('page=\d+', 'page='+str(num) ,driver.current_url))
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='careList careList2 careListk']/ul/li")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='careList careList2 careListk']/ul/li")
    data = []
    for content in content_list:
        name =  content.xpath('./span/a/text()')[0].strip()
        ggstart_time =  content.xpath('./span[last()]/text()')[0].strip()
        href = 'http://zwgk.bengbu.gov.cn/'+content.xpath('./span/a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
        #//td[@id='Paging']/table/tbody/tr/td/font[2]/b
    total_temp = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[@class='page']"))).text
    total_page = re.findall(' \/ (\d+) 页',total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class,'plr16 bgf borderTop2')]")
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
    div = soup.find('div', attrs={'class',re.compile('plr16 bgf borderTop2')})
    return div


data = [
    ["zfcg_gqita_zhao_zhong_gg",
     "http://zwgk.bengbu.gov.cn/new_gkzd.jsp?serialnum=CA&OfNature=400000hint:%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&DwId=86966862&LmId=88063847&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhao_zhong_gg",
     "http://zwgk.bengbu.gov.cn/new_gkzd.jsp?serialnum=CA&OfNature=400000hint:%E6%8B%9B%E6%A0%87%E6%8A%95%E6%A0%87%E4%BF%A1%E6%81%AF&DwId=86966862&LmId=1922532814&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 安徽蚌埠人民政府网
def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省蚌埠市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "anhui_bengbu_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30)
