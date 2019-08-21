import json
import os
import sys

import math
import urllib.parse
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info,est_meta_large



js_dict = {
    '政府采购':'setFileType("1","政府采购","1")',
    '房建工程':'setFileType("201","房建工程","2")',
    '水利工程':'setFileType("202","水利工程","2")',
    '交通工程':'setFileType("203","交通工程","2")',
    '其他工程':'setFileType("204","其他工程","2")',
}

def jump_method(driver):
    jstype = urllib.parse.unquote(driver.current_url.split('#')[-1])

    frame = WebDriverWait(driver,40).until(EC.visibility_of_element_located((By.XPATH,'//iframe[@name="topFrame"]')))

    driver.switch_to.frame(frame)
    driver.execute_script("javascript:jyxx();")
    driver.switch_to_default_content()
    frame = driver.find_element_by_id("mainFrame")
    driver.switch_to.frame(frame)
    js = js_dict.get(jstype)

    driver.execute_script(js)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="w_content_main"]')
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
    div = soup.find('div', class_="w_content_main")

    return div


def f1(driver, num):
    if 'topFrame' in driver.page_source:
        jump_method(driver)

    locator = (By.XPATH, '//table[@id="packTable"]/tbody/tr[not(@style)][1]/td/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('onclick')[-60:]
    locator = (By.XPATH, '//nobr[@id="packTableRowCount"]')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = math.ceil(int(re.findall('(\d+)到',txt)[0])/10)
    if int(cnum) != int(num):
        driver.execute_script("TabAjaxQuery.gotoPage(%s,'packTable');"%num)
        locator = (By.XPATH, '//table[@id="packTable"]/tbody/tr[not(@style)][1]/td/a[not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="packTable"]/tbody/tr[not(@style)]')
    for content in content_list:
        name = content.xpath("./td/a/@title")[0].strip()
        area = content.xpath("./td/a/span/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/font/text()")[0].strip().strip('[').strip(']')
        url = 'http://ggzy.ah.gov.cn/bulletin.do?method=showHomepage&bulletin_id=' + re.findall("\'([^\']+)\'",content.xpath("./td/a/@onclick")[0])[0].strip()
        info = json.dumps({'area':area},ensure_ascii=False)
        temp = [name, ggstart_time, url,info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    if 'topFrame' in driver.page_source:
        jump_method(driver)
    locator = (By.XPATH, '//span[@id="packTablePageCount"]')
    txt = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)',txt)[0]
    driver.quit()
    return int(total_page)




data = [
    #
    ["zfcg_zhaobiao_gg",
     "http://ggzy.ah.gov.cn/login.do?method=beginlogin#政府采购",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'政府采购'}), f2],
    #
    ["gcjs_zhaobiao_fj_gg",
     "http://ggzy.ah.gov.cn/login.do?method=beginlogin#房建工程",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'房建工程'}), f2],
    #
    ["gcjs_zhaobiao_sl_gg",
     "http://ggzy.ah.gov.cn/login.do?method=beginlogin#水利工程",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'水利工程'}), f2],
    #
    ["gcjs_zhaobiao_jt_gg",
     "http://ggzy.ah.gov.cn/login.do?method=beginlogin#交通工程",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'交通工程'}), f2],
    #
    ["gcjs_zhaobiao_qt_gg",
     "http://ggzy.ah.gov.cn/login.do?method=beginlogin#其他工程",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他工程'}), f2],
]



###安徽省公共资源交易监管网
def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="安徽省",**arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':

    # for d in data:
    #
    #     driver = webdriver.Chrome()
    #     url = d[1]
    #     driver.get(url)
    #     df = f1(driver, 2)
    #     #
    #     for u in df.values.tolist()[:4]:
    #         print(f3(driver, u[2]))
    #     driver.get(url)
    #
    #     print(f2(driver))
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "anhuisheng1"],pageloadtimeout=100,num=1,headless=False)
