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

_name_ = 'zhejiang_hangzhou_yuhang_zfcg'


def f1(driver, num):

    driver.get(re.sub('\?page=\d+&', '?page=%s&' % str(num) ,driver.current_url, count=1))
    if num != total_page:
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, "//table[@class='tableBg']/tbody[count(tr)=11]")))
    else:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//table[@class='tableBg']/tbody/tr[2]//a")))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[@class='tableBg']/tbody/tr[position()!=1]")
    data = []
    for content in content_list:
        name =  content.xpath('./td/a/@title')[0].strip()
        ggstart_time =  content.xpath('./td[3]/text()')[0].strip()
        href = content.xpath('./td/a/@href')[0].strip()
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    global total_page
        #//td[@id='Paging']/table/tbody/tr/td/font[2]/b
    total_temp = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//a[@class='last-page']"))).get_attribute('href')
    total_page = int(re.findall('page=(\d+)',total_temp)[0])
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@height='543']//table[@width='95%'][1]/tbody/tr[string-length()>50]")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
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
    div = soup.find('td', height='543')
    return div


data = [
    ["zfcg_gqita_zhong_zhao_bian_gg",
     "http://www.yuhang.gov.cn/was5/web/search?page=1&channelid=241481&searchword=%28s_sitename%3D%27%E6%94%BF%E5%8A%A1%E5%85%AC%E5%BC%80%27%29+and+%28S_DOCCHANNEL%3D2947+or+S_PARENTID%3D2947+or+S_GPID%3D2947+or+S_GGPID%3D2947%29&keyword=%28s_sitename%3D%27%E6%94%BF%E5%8A%A1%E5%85%AC%E5%BC%80%27%29+and+%28S_DOCCHANNEL%3D2947+or+S_PARENTID%3D2947+or+S_GPID%3D2947+or+S_GGPID%3D2947%29&perpage=10&outlinepage=10&&andsen=&total=&orsen=&exclude=&searchscope=&timescope=&timescopecolumn=&orderby=-S_DOCORDERPRI%2C-S_DOCRELTIME",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhong_zhao_bian_gg",
     "http://www.yuhang.gov.cn/was5/web/search?page=1&channelid=241481&searchword=%28s_sitename%3D%27%E6%94%BF%E5%8A%A1%E5%85%AC%E5%BC%80%27%29+and+%28S_DOCCHANNEL%3D2963+or+S_PARENTID%3D2963+or+S_GPID%3D2963+or+S_GGPID%3D2963%29&keyword=%28s_sitename%3D%27%E6%94%BF%E5%8A%A1%E5%85%AC%E5%BC%80%27%29+and+%28S_DOCCHANNEL%3D2963+or+S_PARENTID%3D2963+or+S_GPID%3D2963+or+S_GGPID%3D2963%29&orderby=-S_DOCORDERPRI%2C-S_DOCRELTIME&perpage=10&outlinepage=10&&andsen=&total=&orsen=&exclude=&searchscope=&timescope=&timescopecolumn=&orderby=-S_DOCORDERPRI%2C-S_DOCRELTIME",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 浙江省杭州市余杭区人民政府
def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省杭州市余杭区", **args)
    est_html(conp, f=f3, **args)

# 修改日期：2019/8/16
if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "zhejiang_hangzhou_yuhang_zfcg"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,num=1, headless=False, pageloadstrategy='none', image_show_gg=2,ipNum=0)
