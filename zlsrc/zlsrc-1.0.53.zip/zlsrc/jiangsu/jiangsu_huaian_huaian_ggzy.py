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

_name_ = 'anhui_huainan_ggzy'


def f1(driver, num):
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//table[contains(@id,"Data")]/tbody/tr/td/a'))).get_attribute('href')[-70:]
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@id,'Pager')]//td/font[3]/b"))).text

    if int(num)!=int(cnum):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id,'Data')]/tbody/tr/td/a[not(contains(@href,'%s'))]"%val)))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[contains(@id,'Data')]/tbody/tr")
    data = []
    for content in content_list:
        name =  content.xpath('./td/a/@title')[0].strip()
        ggstart_time =  content.xpath('./td[last()]/text()')[0].strip()
        href = 'http://www.czztb.gov.cn' + content.xpath('./td/a/@href')[0].strip()
        temp = [name, ggstart_time, href]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@id,'Pager')]//td/font[2]/b"))).text

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
    ["gcjs_zhaobiao_fw_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001001/005001001001/MoreInfo.aspx?CategoryNum=005001001001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'房屋建筑'}), f2],

    ["gcjs_zhaobiao_sz_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001001/005001001002/MoreInfo.aspx?CategoryNum=005001001002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市政基础'}), f2],

    ["gcjs_zhaobiao_zx_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001001/005001001003/MoreInfo.aspx?CategoryNum=005001001003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'装饰装修'}), f2],

    ["gcjs_zhaobiao_yl_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001001/005001001004/MoreInfo.aspx?CategoryNum=005001001004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'园林绿化'}), f2],

    ["gcjs_zhaobiao_sb_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001001/005001001005/MoreInfo.aspx?CategoryNum=005001001005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'设备采购'}), f2],

    ["gcjs_zhaobiao_qt_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001001/005001001006/MoreInfo.aspx?CategoryNum=005001001006",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '其他'}), f2],
#########
    ["gcjs_kongzhijia_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001003/MoreInfo.aspx?CategoryNum=005001003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ##########
    ["gcjs_zhongbiaohx_fw_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001004/005001004001/MoreInfo.aspx?CategoryNum=005001004001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '房屋建筑'}), f2],

    ["gcjs_zhongbiaohx_sz_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001004/005001004002/MoreInfo.aspx?CategoryNum=005001004002",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '市政基础'}), f2],

    ["gcjs_zhongbiaohx_zx_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001004/005001004003/MoreInfo.aspx?CategoryNum=005001004003",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '装饰装修'}), f2],

    ["gcjs_zhongbiaohx_yl_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001004/005001004004/MoreInfo.aspx?CategoryNum=005001004004",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '园林绿化'}), f2],

    ["gcjs_zhongbiaohx_sb_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001004/005001004005/MoreInfo.aspx?CategoryNum=005001004005",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '设备采购'}), f2],

    ["gcjs_zhongbiaohx_jl_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001004/005001004006/MoreInfo.aspx?CategoryNum=005001004006",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '工程监理'}), f2],

    ["gcjs_zhongbiaohx_qt_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001004/005001004007/MoreInfo.aspx?CategoryNum=005001004007",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '其他'}), f2],
    ###
    ["gcjs_zhongbiao_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001005/MoreInfo.aspx?CategoryNum=005001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ###
    ["gcjs_zsjg_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005001/005001006/MoreInfo.aspx?CategoryNum=005001006",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ############
    ["zfcg_zhaobiao_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005002/005002001/MoreInfo.aspx?CategoryNum=005002001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005002/005002002/MoreInfo.aspx?CategoryNum=005002002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005002/005002003/MoreInfo.aspx?CategoryNum=005002003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005002/005002004/MoreInfo.aspx?CategoryNum=005002004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #############
    ["gcjs_gqita_gg",
     "http://www.czztb.gov.cn/czztb/jyxx/005004/MoreInfo.aspx?CategoryNum=005004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'项目经理变更公示'}), f2],

]

#淮安区公共资源
def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省淮安市淮安区", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "anhui_huainan_ggzy"]
    # driver = webdriver.Chrome()
    # driver.get(
    #     'http://szggzy.shuozhou.gov.cn/moreInfoController.do?getMoreNoticeInfo&rows=20&page=1&dateFlag=&tableName=&projectRegion=&projectName=&beginReceivetime=&endReceivetime=')
    # print(f2(driver))
    #
    # f1(driver, 1)
    # f1(driver, 21)
    work(conp,total=30)
