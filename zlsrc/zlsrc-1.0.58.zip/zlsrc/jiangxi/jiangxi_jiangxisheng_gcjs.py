import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta_large
from zlsrc.util.etl import est_meta, est_html, add_info



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]/tbody/tr/td/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-60:]

    locator = (By.XPATH, '//font[@color="blue"][1]/b')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    cnum = re.findall('(\d+)', txt)[0]

    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)

        locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]/tbody/tr/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="MoreInfoList1_DataGrid1"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td[2]/a/@title")[0].strip()
        ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        url = 'http://www.jxgzwztb.com' + content.xpath("./td[2]/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//font[@color="blue"][2]/b')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    total_page = re.findall('(\d+)', txt)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["gcjs_zhaobiao_gc_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007001/007001002/MoreInfo.aspx?CategoryNum=007001002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"工程类"}), f2],
    #
    ["gcjs_biangeng_gc_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007001/007001004/MoreInfo.aspx?CategoryNum=007001004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"工程类"}), f2],
    #
    ["gcjs_zhongbiao_gc_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007001/007001003/MoreInfo.aspx?CategoryNum=007001003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"工程类"}), f2],
    #
    ["gcjs_zgysjg_gc_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007001/007001001/MoreInfo.aspx?CategoryNum=007001001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"工程类"}), f2],


    #
    ["gcjs_zhaobiao_hw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007002/007002002/MoreInfo.aspx?CategoryNum=007002002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"货物类"}), f2],
    #
    ["gcjs_biangeng_hw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007002/007002004/MoreInfo.aspx?CategoryNum=007002004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"货物类"}), f2],
    #
    ["gcjs_zhongbiao_hw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007002/007002003/MoreInfo.aspx?CategoryNum=007002003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"货物类"}), f2],
    #
    ["gcjs_zgysjg_hw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007002/007002001/MoreInfo.aspx?CategoryNum=007002001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"货物类"}), f2],



    #
    ["gcjs_zhaobiao_fw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007003/007003002/MoreInfo.aspx?CategoryNum=007003002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"服务类"}), f2],
    #
    ["gcjs_biangeng_fw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007003/007003004/MoreInfo.aspx?CategoryNum=007003004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"服务类"}), f2],
    #
    ["gcjs_zhongbiao_fw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007003/007003003/MoreInfo.aspx?CategoryNum=007003003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"服务类"}), f2],
    #
    ["gcjs_zgysjg_fw_gg",
     "http://www.jxgzwztb.com/gzwzbw/ztpd/007003/007003001/MoreInfo.aspx?CategoryNum=007003001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"服务类"}), f2],



]


def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="江西省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    # url = "http://www.ahtba.org.cn/Notice/jiangxiNoticeSearch?spid=714&scid=597&srcode=&sttype=&stime=36500&stitle=&sCompanyName=&isPageBarSearch=0&pageNum=1&pageSize=15"
    for d in data:

        driver = webdriver.Chrome()
        driver.get(d[1])
        df = f1(driver, 2)
        for ur in df.values.tolist():
            print(f3(driver, ur[2]))
        driver.get(d[1])
        print(f2(driver))

    #
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "jiangxisheng"])
